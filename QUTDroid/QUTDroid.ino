#include <PinChangeInterrupt.h>
#include <ArduinoJson.h>
#include "ESC.h"
#include <Servo.h>

/* 
UTS Robotics Society - QUT DRC Motor Controller
Version 1.1 - June 2018
Contributers: Kwang Baik, Jason Ho, James Ryan  
*/

/*
JSON Packet Structure
 
Example: {"Mode" : "Drive","Throttle" : "255","Direction" : "1","Steering" : "180"}

"Mode" can be:
	Driving - Normal Operation and Clears Command Watchdog - Additional Arg Below:
		Throttle - Ranges from 0 - 255 representing stopped - full speed
		Direction - Switchs the "gear" of the car where:
			0 = Netural - All Stop
			1 = Forward
			2 = Backward
		Steering - Ranges from 0 - 180 and represents steerring servo angle 

	Watchdog - Clears Command Watchdog Only - No Additional Args

	Stop - Stops All Motion and Sets Steering to 90 (straight) - No Additional Args

 */

// Start User Settings

// Core Settings

#define LED_PIN 13

#define STEERING_SERVO_DATA_PIN 10
#define THROTTLE_ESC_DATA_PIN 11

#define THROTTLE_SPEED_PERIOD_MIN 1000 // Set the Minimum Speed in microseconds
#define THROTTLE_SPEED_PERIOD_MAX 2000 // Set the Minimum Speed in microseconds
#define THROTTLE_SPEED_PERIOD_ARM 500
#define THROTTLE_SPEED_LIMITED_MAX 1600
#define THROTTLE_SPEED_LIMITED_MIN 1350 //Us

// Serial Comms Settings

#define COMMS_BAUD_RATE 115200
#define COMMS_SERIAL_TIMEOUT 10 // Serial Library timeout
#define COMMS_COMMAND_TIMEOUT 10000 // Safety Timeout - Stops car if no command has been RX'ed in this time (in milliseconds)

// Manual RC Control Setting

#define MANUAL_RC_ENABLED // Turns on Module

#define MANUAL_RC_ON_BOARD_ENABLE_PIN 5

#define MANUAL_RC_STEERING_PIN  2
#define MANUAL_RC_THROTTLE_PIN	3
#define MANUAL_RC_MODE_AND_E_STOP_KILL_PIN 4  

#define MANUAL_RC_RECEIVER_MAX_PERIOD 2000
#define MANUAL_RC_RECEIVER_MIN_PERIOD 1000

#define MANUAL_RC_SWITCH_STATE_UP_LIMIT 1000
#define MANUAL_RC_SWITCH_STATE_DOWN_LIMIT 1750

// Bling Settings

// End User Settings

#ifndef THROTTLE_SPEED_LIMITED_MAX
#define THROTTLE_SPEED_LIMITED_MAX THROTTLE_SPEED_PERIOD_MAX
#endif

#ifndef THROTTLE_SPEED_LIMITED_MIN
#define THROTTLE_SPEED_LIMITED_MIN THROTTLE_SPEED_PERIOD_MIN
#endif 

Servo SteeringServo; 
ESC ThrottleController(THROTTLE_ESC_DATA_PIN, THROTTLE_SPEED_PERIOD_MIN, THROTTLE_SPEED_PERIOD_MAX, THROTTLE_SPEED_PERIOD_ARM);

StaticJsonBuffer<200> CommsJSONBuffer;
bool CommandWatchdogEnabled = false;
unsigned long commandWatchdogTimer;

struct DriveParameters
{
	enum Direction : unsigned char
	{
		Forward = 1,
		Backward = 2,
		Neutral = 0
	};

	Direction travelDirection = Neutral;
	unsigned char throttle = 0;
	unsigned char steeringAngle = 90;

};

DriveParameters DroidCar;

void SerialCommsSetup()
{
	Serial.begin(COMMS_BAUD_RATE);
	Serial.setTimeout(COMMS_SERIAL_TIMEOUT);
	CommandWatchdogEnabled = true;
}

void SteeringSetup()
{
	SteeringServo.attach(STEERING_SERVO_DATA_PIN);
	SteeringServo.write(90);
}

void ThrottleSetup()
{
	ThrottleController.arm();
	ThrottleController.speed((THROTTLE_SPEED_PERIOD_MIN + THROTTLE_SPEED_PERIOD_MAX) / 2);
}

//---------------------------------------//

void SafetyStop()
{
	DroidCar.throttle = 0;
	DroidCar.travelDirection = DroidCar.Neutral;
	DroidCar.steeringAngle = 90;
}

void WatchdogCheck()
{
	if (millis() - commandWatchdogTimer > COMMS_COMMAND_TIMEOUT && CommandWatchdogEnabled == true)
	{
		SafetyStop();
		digitalWrite(LED_PIN, HIGH);
	}
	else
	{
		digitalWrite(LED_PIN, LOW);
	}
}

void SerialCommandProcessor()
{
	if (Serial.available() > 0)
	{
		char commandBuffer[200];
		Serial.readBytesUntil('\r', commandBuffer, sizeof(commandBuffer));
		JsonObject& Packet = CommsJSONBuffer.parseObject(commandBuffer);

		if (Packet.success()) {
			if (Packet["Mode"] == "Drive")
			{
				//Serial.println("RX Drive");
				DroidCar.throttle = Packet["Throttle"];
				unsigned char directionRaw = Packet["Direction"];
				DroidCar.travelDirection = static_cast<DriveParameters::Direction>(directionRaw);
				DroidCar.steeringAngle = Packet["Steering"];
				//Serial.println(String(DroidCar.throttle) + " | " + String(DroidCar.throttle) + " | " + String(directionRaw) +" | " + String(DroidCar.steeringAngle));
			}
			else if (Packet["Mode"] == "Stop")
			{
				SafetyStop();

			}
			commandWatchdogTimer = millis();
		}

		while (Serial.available() > 0)
		{
			Serial.read(); // clear buffer
		}

		CommsJSONBuffer.clear();
	}
}

void DriveUpdate() {

	SteeringServo.write(constrain(DroidCar.steeringAngle, 0, 180));
	
	unsigned int speedPeriodRaw;

	switch (DroidCar.travelDirection)
	{
	case DriveParameters::Forward: 
		speedPeriodRaw = map(DroidCar.throttle, 0, 255, (THROTTLE_SPEED_PERIOD_MIN + THROTTLE_SPEED_PERIOD_MAX) / 2 , THROTTLE_SPEED_PERIOD_MIN);
		break;
	case DriveParameters::Backward: 
		speedPeriodRaw = map(DroidCar.throttle, 0, 255, (THROTTLE_SPEED_PERIOD_MIN + THROTTLE_SPEED_PERIOD_MAX) / 2, THROTTLE_SPEED_PERIOD_MAX);
		break;
	case DriveParameters::Neutral: 
		speedPeriodRaw = (THROTTLE_SPEED_PERIOD_MIN + THROTTLE_SPEED_PERIOD_MAX) / 2;
		break;
	default:
		break;
	}
	ThrottleController.speed(constrain(speedPeriodRaw, THROTTLE_SPEED_LIMITED_MIN, THROTTLE_SPEED_LIMITED_MAX));
	
}

#ifdef MANUAL_RC_ENABLED

#include <PinChangeInterrupt.h>

unsigned long SteeringTimer;
unsigned long ThrottleTimer;
unsigned long ActivateTimer;

unsigned long SteeringPeriod;
unsigned long ThrottlePeriod;
unsigned long ActivatePeriod;

struct RCControlModel
{
	unsigned char switch1State;
	unsigned int switch1Period;
	unsigned int steeringPeriod;
	unsigned int throttlePeriod;
};

RCControlModel RCController1;

void ManualControlTimerInterrupt(unsigned long *TimerVariable, unsigned long *FinalPeriod, bool State)
{
	if (State == true)
	{
		*TimerVariable = micros();
	}
	else
	{
		*FinalPeriod = micros() - *TimerVariable;
	}
}

void ManualControlSteeringInputInterrupt()
{
	ManualControlTimerInterrupt(&SteeringTimer, &SteeringPeriod, digitalRead(MANUAL_RC_STEERING_PIN));
	RCController1.steeringPeriod = SteeringPeriod;
}

void ManualControlThrottleInputInterrupt()
{
	ManualControlTimerInterrupt(&ThrottleTimer, &ThrottlePeriod, digitalRead(MANUAL_RC_THROTTLE_PIN));
	RCController1.throttlePeriod = ThrottlePeriod;
}

void ManualControlActivateInputInterrupt()
{
	ManualControlTimerInterrupt(&ActivateTimer, &ActivatePeriod, digitalRead(MANUAL_RC_MODE_AND_E_STOP_KILL_PIN));
	RCController1.switch1Period = ActivatePeriod;

	if (RCController1.switch1Period <= MANUAL_RC_SWITCH_STATE_UP_LIMIT)
	{
		RCController1.switch1State = 2;
	}
	else if (RCController1.switch1Period > MANUAL_RC_SWITCH_STATE_UP_LIMIT && RCController1.switch1Period < MANUAL_RC_SWITCH_STATE_DOWN_LIMIT)
	{
		RCController1.switch1State = 1;
	}
	else
	{
		RCController1.switch1State = 0;
	}

}

void ManualControlSetup()
{
	pinMode(MANUAL_RC_MODE_AND_E_STOP_KILL_PIN, INPUT_PULLUP);
	pinMode(MANUAL_RC_STEERING_PIN, INPUT_PULLUP);
	pinMode(MANUAL_RC_THROTTLE_PIN, INPUT_PULLUP);

	pinMode(MANUAL_RC_ON_BOARD_ENABLE_PIN, INPUT_PULLUP);

	attachInterrupt(digitalPinToInterrupt(MANUAL_RC_STEERING_PIN), ManualControlSteeringInputInterrupt, CHANGE);
	attachInterrupt(digitalPinToInterrupt(MANUAL_RC_THROTTLE_PIN), ManualControlThrottleInputInterrupt, CHANGE);
	attachPCINT(digitalPinToPCINT(MANUAL_RC_MODE_AND_E_STOP_KILL_PIN), ManualControlActivateInputInterrupt, CHANGE);
}

void ManualControlProcessor()
{
	DroidCar.steeringAngle = map(RCController1.steeringPeriod, MANUAL_RC_RECEIVER_MIN_PERIOD, MANUAL_RC_RECEIVER_MAX_PERIOD, 0, 180);
	if (RCController1.throttlePeriod > (MANUAL_RC_RECEIVER_MIN_PERIOD + MANUAL_RC_RECEIVER_MAX_PERIOD) / 2)
	{
		DroidCar.travelDirection = DroidCar.Forward;
		DroidCar.throttle = constrain(map(RCController1.throttlePeriod, (MANUAL_RC_RECEIVER_MIN_PERIOD + MANUAL_RC_RECEIVER_MAX_PERIOD) / 2, MANUAL_RC_RECEIVER_MAX_PERIOD, 0, 255), 0, 255);
	}
	else if (RCController1.throttlePeriod < (MANUAL_RC_RECEIVER_MIN_PERIOD + MANUAL_RC_RECEIVER_MAX_PERIOD) / 2)
	{
		DroidCar.travelDirection = DroidCar.Backward;
		DroidCar.throttle = constrain(map(RCController1.throttlePeriod, MANUAL_RC_RECEIVER_MIN_PERIOD, (MANUAL_RC_RECEIVER_MIN_PERIOD + MANUAL_RC_RECEIVER_MAX_PERIOD) / 2, 255, 0), 0,255);
	}
	else
	{
		DroidCar.travelDirection = DroidCar.Neutral;
		DroidCar.throttle = 0;
	}
}

#endif // MANUAL_RC_ENABLED

void setup() 
{
	SerialCommsSetup();
	ThrottleSetup();
	SteeringSetup();
	
#ifdef MANUAL_RC_ENABLED
	ManualControlSetup();
#endif // MANUAL_RC_ENABLED
}

void loop() {
	
	
#ifdef MANUAL_RC_ENABLED
	if (digitalRead(MANUAL_RC_ON_BOARD_ENABLE_PIN) == HIGH && RCController1.switch1State == 0)
	{
		CommandWatchdogEnabled = true;
		SafetyStop();
	}
	else if (digitalRead(MANUAL_RC_ON_BOARD_ENABLE_PIN) == HIGH && RCController1.switch1State == 1) {
		CommandWatchdogEnabled = false;
		ManualControlProcessor();
	}
	else
	{
		CommandWatchdogEnabled = true;
		SerialCommandProcessor();
	}
#else
	SerialCommandProcessor();
#endif // MANUAL_RC_ENABLED
	WatchdogCheck();
	DriveUpdate();
}   



