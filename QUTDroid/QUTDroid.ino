
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
 
Example: {"Mode" : "Drive","Throttle" : "255","Direction" : "0","Steering" : "180"}

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

#define LED_PIN 13

#define STEERING_SERVO_DATA_PIN 10
#define THROTTLE_ESC_DATA_PIN 11

#define THROTTLE_SPEED_PERIOD_MIN 1000 // Set the Minimum Speed in microseconds
#define THROTTLE_SPEED_PERIOD_MAX 2000 // Set the Minimum Speed in microseconds
#define THROTTLE_SPEED_PERIOD_ARM 500
#define THROTTLE_SPEED_LIMITED_MAX 1600
#define THROTTLE_SPEED_LIMITED_MIN 1350 //Us


#define COMMS_BAUD_RATE 115200
#define COMMS_SERIAL_TIMEOUT 10 // Serial Library timeout
#define COMMS_COMMAND_TIMEOUT 10000 // Safety Timeout - Stops car if no command has been RX'ed in this time (in milliseconds)

// End User Settings

#ifndef THROTTLE_SPEED_LIMITED_MAX
#define THROTTLE_SPEED_LIMITED_MAX THROTTLE_SPEED_PERIOD_MAX
#endif

#ifndef THROTTLE_SPEED_LIMITED_MIN
#define THROTTLE_SPEED_LIMITED_MIN THROTTLE_SPEED_PERIOD_MIN
#endif 

Servo SteeringServo; 
ESC ThrottleController (THROTTLE_ESC_DATA_PIN, THROTTLE_SPEED_PERIOD_MIN, THROTTLE_SPEED_PERIOD_MAX, THROTTLE_SPEED_PERIOD_ARM);

StaticJsonBuffer<200> CommsJSONBuffer;
bool CommandWatchdogEnabled = false;
unsigned long commandWatchdogTimer;

struct DriveParameters
{
	enum Direction : unsigned char
	{
		Foward = 1,
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
	ThrottleController.speed(0);
}

//---------------------------------------//

void SafetyStop()
{
	DroidCar.throttle = 0;
	DroidCar.travelDirection = DroidCar.Neutral;
	DroidCar.steeringAngle = 90;
}

void CommandProcessor()
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

	//Watchdog Check

	if (millis() - commandWatchdogTimer > COMMS_COMMAND_TIMEOUT)
	{
		SafetyStop();
		digitalWrite(LED_PIN, HIGH);
	}
	else
	{
		digitalWrite(LED_PIN, LOW);
	}

}

void DriveUpdate() {

	SteeringServo.write(constrain(DroidCar.steeringAngle, 0, 180));
	
	unsigned int speedPeriodRaw;

	switch (DroidCar.travelDirection)
	{
	case DriveParameters::Foward: 
		speedPeriodRaw = map(DroidCar.throttle, 0, 255, (THROTTLE_SPEED_PERIOD_MIN + THROTTLE_SPEED_PERIOD_MAX) / 2 , THROTTLE_SPEED_PERIOD_MAX);
		break;
	case DriveParameters::Backward: 
		speedPeriodRaw = map(DroidCar.throttle, 0, 255, (THROTTLE_SPEED_PERIOD_MIN + THROTTLE_SPEED_PERIOD_MAX) / 2, THROTTLE_SPEED_PERIOD_MIN);
		break;
	case DriveParameters::Neutral: 
		speedPeriodRaw = (THROTTLE_SPEED_PERIOD_MIN + THROTTLE_SPEED_PERIOD_MAX) / 2;
		break;
	default:
		break;
	}
	ThrottleController.speed(constrain(speedPeriodRaw, THROTTLE_SPEED_LIMITED_MIN, THROTTLE_SPEED_LIMITED_MAX));
	
}

void setup() 
{
	SerialCommsSetup();
	SteeringSetup();
	ThrottleSetup();
}
void loop() {
	CommandProcessor();
	DriveUpdate();
}   



