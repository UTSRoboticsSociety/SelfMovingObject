
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

#define SERIAL_REPORT_ENABLED
#define SERIAL_REPORT_TX_PIN 13
#define SERIAL_REPORT_RX_PIN 12
#define SERIAL_REPORT_BAUD 9600
#define SERIAL_REPORT_INTERVAL 100

#define STEERING_SERVO_DATA_PIN 9
#define THROTTLE_ESC_DATA_PIN 6

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

//#define MANUAL_RC_STEERING_PIN  2
//#define MANUAL_RC_THROTTLE_PIN	3
//#define MANUAL_RC_MODE_AND_E_STOP_KILL_PIN 4  

#define PPM_DATA_PIN 2
#define PPM_CHANNELS 10

#define MANUAL_RC_STEERING_CH  1
#define MANUAL_RC_THROTTLE_CH	2
#define MANUAL_RC_MODE_AND_E_STOP_KILL_CH 5  

#define MANUAL_RC_RECEIVER_MAX_PERIOD 2000
#define MANUAL_RC_RECEIVER_MIN_PERIOD 1000

#define MANUAL_RC_SWITCH_STATE_UP_LIMIT 1000
#define MANUAL_RC_SWITCH_STATE_DOWN_LIMIT 1750

// Bling Settings
#ifdef SERIAL_REPORT_ENABLED
//SoftwareSerial SerialReport(SERIAL_REPORT_RX_PIN, SERIAL_REPORT_TX_PIN);
#endif // DEBUG


// End User Settings

#ifndef THROTTLE_SPEED_LIMITED_MAX
#define THROTTLE_SPEED_LIMITED_MAX THROTTLE_SPEED_PERIOD_MAX
#endif

#ifndef THROTTLE_SPEED_LIMITED_MIN
#define THROTTLE_SPEED_LIMITED_MIN THROTTLE_SPEED_PERIOD_MIN
#endif 

Servo SteeringServo;
ESC ThrottleController(THROTTLE_ESC_DATA_PIN, THROTTLE_SPEED_PERIOD_MIN, THROTTLE_SPEED_PERIOD_MAX, THROTTLE_SPEED_PERIOD_ARM);

//Adafruit_NeoPixel Indicators(NEOPIXEL_QUANTITY, NEOPIXEL_PIN);

StaticJsonBuffer<200> CommsJSONBuffer;
bool CommandWatchdogEnabled = false;
unsigned long commandWatchdogTimer;

struct DriveParameters
{
	unsigned char driveMode = 0;

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

struct I2CTransport
{
	DriveParameters DriveData;
};

DriveParameters DroidCar;
I2CTransport dataContainer;

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
		//digitalWrite(LED_PIN, HIGH);
	}
	else
	{
		//digitalWrite(LED_PIN, LOW);
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
		speedPeriodRaw = map(DroidCar.throttle, 0, 255, (THROTTLE_SPEED_PERIOD_MIN + THROTTLE_SPEED_PERIOD_MAX) / 2, THROTTLE_SPEED_PERIOD_MIN);
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

#include <PPMReader.h>

unsigned long SteeringTimer;
unsigned long ThrottleTimer;
unsigned long ActivateTimer;

unsigned long SteeringPeriod;
unsigned long ThrottlePeriod;
unsigned long ActivatePeriod;

unsigned int PPMPeriods[PPM_CHANNELS];

struct RCControlModel
{
	unsigned char switch1State;
	unsigned int switch1Period;
	unsigned int steeringPeriod;
	unsigned int throttlePeriod;
};

RCControlModel RCController1;

PPMReader ppm(PPM_DATA_PIN, PPM_CHANNELS);

void PPMUpdater()
{
	for (int i = 0; i < PPM_CHANNELS; i++)
	{
		PPMPeriods[i] = ppm.latestValidChannelValue(i,0);
	}
	RCController1.steeringPeriod = PPMPeriods[MANUAL_RC_STEERING_CH];
	RCController1.throttlePeriod = PPMPeriods[MANUAL_RC_THROTTLE_CH];
	RCController1.switch1Period = PPMPeriods[MANUAL_RC_MODE_AND_E_STOP_KILL_CH];

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
	//pinMode(MANUAL_RC_MODE_AND_E_STOP_KILL_PIN, INPUT_PULLUP);
	//pinMode(MANUAL_RC_STEERING_PIN, INPUT_PULLUP);
	//pinMode(MANUAL_RC_THROTTLE_PIN, INPUT_PULLUP);
	pinMode(MANUAL_RC_ON_BOARD_ENABLE_PIN, INPUT_PULLUP);
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
		DroidCar.throttle = constrain(map(RCController1.throttlePeriod, MANUAL_RC_RECEIVER_MIN_PERIOD, (MANUAL_RC_RECEIVER_MIN_PERIOD + MANUAL_RC_RECEIVER_MAX_PERIOD) / 2, 255, 0), 0, 255);
	}
	else
	{
		DroidCar.travelDirection = DroidCar.Neutral;
		DroidCar.throttle = 0;
	}
}

#endif // MANUAL_RC_ENABLED

#ifdef SERIAL_REPORT_ENABLED

#include <Wire.h>

void SerialReportSetup()
{
	Wire.begin(0);
}

void SerialReportService()
{
	static unsigned long serialReportTimer;
	if (millis() - serialReportTimer >= SERIAL_REPORT_INTERVAL)
	{
		Wire.beginTransmission(0x10);
		if (!Wire.endTransmission())
		{
			dataContainer.DriveData = DroidCar;
			Wire.beginTransmission(0x10);
			Wire.write(reinterpret_cast<unsigned char*>(&dataContainer), sizeof(dataContainer));
			Wire.endTransmission();
		}

		serialReportTimer = millis();
	}
}

#endif // SERIAL_REPORT_ENABLED


void setup()
{
	SerialCommsSetup();
	ThrottleSetup();
	SteeringSetup();

#ifdef MANUAL_RC_ENABLED
	ManualControlSetup();
#endif // MANUAL_RC_ENABLED

#ifdef SERIAL_REPORT_ENABLED
	SerialReportSetup();
#endif // SERIAL_REPORT_ENABLED
}

void loop() {
#ifdef MANUAL_RC_ENABLED
	PPMUpdater();
	if (digitalRead(MANUAL_RC_ON_BOARD_ENABLE_PIN) == HIGH && RCController1.switch1State == 2)
	{
		DroidCar.driveMode = 0;
		CommandWatchdogEnabled = true;
		SafetyStop();
	}
	else if (digitalRead(MANUAL_RC_ON_BOARD_ENABLE_PIN) == HIGH && RCController1.switch1State == 1) {
		DroidCar.driveMode = 1;
		CommandWatchdogEnabled = false;
		ManualControlProcessor();
	}
	else
	{
		DroidCar.driveMode = 2;
		CommandWatchdogEnabled = true;
		SerialCommandProcessor();
	}
#else
	SerialCommandProcessor();
#endif // MANUAL_RC_ENABLED
	WatchdogCheck();
	DriveUpdate();
#ifdef SERIAL_REPORT_ENABLED
	SerialReportService();
#endif // SERIAL_REPORT_ENABLED

}
