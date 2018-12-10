/*
 Name:		QUT_Droid_Bling_MCU.ino
 Created:	12/8/2018 3:24:53 PM
 Author:	jason
*/


#include <Wire.h>
#include <Adafruit_NeoPixel.h>

#define NEOPIXEL_PIN 11
#define NEOPIXEL_QUANTITY 28

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

Adafruit_NeoPixel Indicators(NEOPIXEL_QUANTITY, NEOPIXEL_PIN);

// the setup function runs once when you press reset or power the board

void wireRx(int bytes)
{
	if (Wire.available() > 2)
	{
		Wire.readBytes(reinterpret_cast<unsigned char*>(&dataContainer), sizeof(dataContainer));
		DroidCar = dataContainer.DriveData;
	}
}

void setup() {
	
	Indicators.begin();
	Indicators.setBrightness(150);
	for (int i = 0; i < NEOPIXEL_QUANTITY; i++)
	{
		Indicators.setPixelColor(i,250,0,0);
	}

	Indicators.show();
	Wire.begin(0x10);
	Wire.onReceive(wireRx);
}

void TurnIndicatorService()
{
	static unsigned long blinker;
	static bool blinkState;
	if (millis() - blinker >= 250)
	{
		blinkState = !blinkState;
		blinker = millis();
	}
	if (DroidCar.driveMode == 0 && blinkState == true)
	{
		Indicators.setPixelColor(0, 250, 50, 0);
		Indicators.setPixelColor(1, 250, 50, 0);
    Indicators.setPixelColor(27, 250, 50, 0);


		Indicators.setPixelColor(4, 250, 50, 0);
		Indicators.setPixelColor(5, 250, 50, 0);
    Indicators.setPixelColor(22, 250, 50, 0);

	}
	else if (DroidCar.steeringAngle < 80 && blinkState == true)
	{
		Indicators.setPixelColor(0, 250, 50, 0);
		Indicators.setPixelColor(1, 250, 50, 0);
    Indicators.setPixelColor(27, 250, 50, 0);


		Indicators.setPixelColor(4, 0, 0, 0);
		Indicators.setPixelColor(5, 0, 0, 0);
    Indicators.setPixelColor(22, 0, 0, 0);

	}
	else if (DroidCar.steeringAngle > 100 && blinkState == true) {
		Indicators.setPixelColor(0, 0, 0, 0);
		Indicators.setPixelColor(1, 0, 0, 0);
    Indicators.setPixelColor(27, 0, 0, 0);


		Indicators.setPixelColor(4, 250, 50, 0);
		Indicators.setPixelColor(5, 250, 50, 0);
    Indicators.setPixelColor(22, 250, 50, 0);

	}
	else
	{
		Indicators.setPixelColor(0, 0, 0, 0);
		Indicators.setPixelColor(1, 0, 0, 0);
    Indicators.setPixelColor(27, 0, 0, 0);


		Indicators.setPixelColor(4, 0, 0, 0);
		Indicators.setPixelColor(5, 0, 0, 0);
    Indicators.setPixelColor(22, 0, 0, 0);

	}

}

void SetUnderLights(int r,int g,int b){
  for(int i = 6; i < (6 + 16); i ++){
      Indicators.setPixelColor(i, r, g, b);
  }
}

void BrakeIndicatorService()
{
	static bool flasher;
	static unsigned long flasherTimer;

	if (millis() - flasherTimer >= 250)
	{
		flasher = !flasher;
		flasherTimer = millis();
	}

	if ((DroidCar.throttle < 30 && DroidCar.travelDirection == DroidCar.Forward) || (DroidCar.throttle < 20 && DroidCar.travelDirection == DroidCar.Backward) || (DroidCar.travelDirection == DroidCar.Neutral))
	{
		Indicators.setPixelColor(2, 250, 0, 0);
		Indicators.setPixelColor(3, 250, 0, 0);
    //Indicators.setPixelColor(22, 250, 0, 0);
    Indicators.setPixelColor(23, 250, 0, 0);
    Indicators.setPixelColor(24, 250, 0, 0);
    Indicators.setPixelColor(25, 250, 0, 0);
    Indicators.setPixelColor(26, 250, 0, 0);
    //Indicators.setPixelColor(27, 250, 0, 0);
   
    
   
	}
	else if (DroidCar.throttle > 20 && DroidCar.travelDirection == DroidCar.Backward) {
		Indicators.setPixelColor(2, 250, 250, 250);
		Indicators.setPixelColor(3, 250, 250, 250);
    //Indicators.setPixelColor(22, 250, 250, 250);
    Indicators.setPixelColor(23, 250, 250, 250);
    Indicators.setPixelColor(24, 250, 250, 250);
    Indicators.setPixelColor(25, 250, 250, 250);
    Indicators.setPixelColor(26, 250, 250, 250);
    //Indicators.setPixelColor(27, 250, 250, 250);
	}
	else if (DroidCar.throttle >= 30 && DroidCar.travelDirection == DroidCar.Forward)
	{
		if (flasher)
		{
			Indicators.setPixelColor(2, 255, 0, 0);
			Indicators.setPixelColor(3, 0, 0, 255);
     // Indicators.setPixelColor(22, 255, 0, 0);
      Indicators.setPixelColor(23, 0, 0, 255);
      Indicators.setPixelColor(24, 255, 0, 0);
      Indicators.setPixelColor(25, 0, 0, 255);
      Indicators.setPixelColor(26, 255, 0, 0);
      //Indicators.setPixelColor(27, 0, 0, 255);

		}
		else
		{
			Indicators.setPixelColor(2, 0, 0, 255);
			Indicators.setPixelColor(3, 255, 0, 0);
      //Indicators.setPixelColor(22, 0, 0, 255);
      Indicators.setPixelColor(23, 255, 0, 0);
      Indicators.setPixelColor(24, 0, 0, 255);
      Indicators.setPixelColor(25, 255, 0, 0);
      Indicators.setPixelColor(26, 0, 0, 255);
      //Indicators.setPixelColor(27, 255, 0, 0);
		}
	}
	else
	{
		Indicators.setPixelColor(2, 0, 0, 0);
		Indicators.setPixelColor(3, 0, 0, 0);
    //Indicators.setPixelColor(22, 0, 0, 0);
    Indicators.setPixelColor(23, 0, 0, 0);
    Indicators.setPixelColor(24, 0, 0, 0);
    Indicators.setPixelColor(25, 0, 0, 0);
    Indicators.setPixelColor(26, 0, 0, 0);
    //Indicators.setPixelColor(27, 0, 0, 0);
	}
}

// the loop function runs over and over again until power down or reset
void loop() {

	switch (DroidCar.driveMode)
	{
	case 0:
		TurnIndicatorService();
		Indicators.setPixelColor(2, 255, 0, 0);
		Indicators.setPixelColor(3, 255, 0, 0);
		break;
	case 1:
		TurnIndicatorService();
		BrakeIndicatorService();
		break;
	case 2:
		TurnIndicatorService();
		BrakeIndicatorService();
		break;
	default:
		for (int i = 0; i < NEOPIXEL_QUANTITY; i++)
		{
			Indicators.setPixelColor(i, 0, 0, 0);
		}
		break;
	}

  double currentTime = millis();
  int redCol = int ((sin(currentTime / (911.0 / 3)) + 1) * 100.0);
  int greenCol = int((sin(currentTime / (533.0 / 3)) + 1) * 100.0);
  int blueCol = int ((sin(currentTime / (747.0 / 3)) + 1) * 100.0);
  
  SetUnderLights(redCol, greenCol, blueCol);

	Indicators.show();
}
