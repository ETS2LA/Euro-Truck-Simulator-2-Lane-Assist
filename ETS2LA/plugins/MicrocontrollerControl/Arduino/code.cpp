#define 	SERIAL_BUFFER_LEN   1024    // Define your buffer


void setup ()
{
	Serial1.setTimeout  (50);   // Set your timeout
	Serial1.begin(115200);      // Set your bitrate
}

void loop ()
{
	char SerialBuffer          [SERIAL_BUFFER_LEN];
	int iResult;

  // Read from Serial1
  if (Serial1.available())
  {                
      memset (SerialBuffer, 0, sizeof(SerialBuffer));
      iResult = Serial1.readBytes(SerialBuffer, SERIAL_BUFFER_LEN);
      if (iResult > 0){
        println(SerialBuffer);
      }
  }
}