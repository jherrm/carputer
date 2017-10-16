#include <Servo.h>

#define MOVEMENT_DELAY 0

#define RIGHT_SERVO_PIN 10
#define LEFT_SERVO_PIN 9

#define RIGHT_START 85
#define RIGHT_END 133

#define LEFT_START 85
#define LEFT_END 47

Servo right;
Servo left;

int rightPos = 0;
int leftPos = 0;

int INC = 2;

void flipRight() {
  for (rightPos = RIGHT_START; rightPos <= RIGHT_END; rightPos += INC) {
    // in steps of 1 degree
    right.write(rightPos);
    delay(MOVEMENT_DELAY);
  }
}

void releaseRight() {
  for (rightPos = RIGHT_END; rightPos >= RIGHT_START; rightPos -= INC) {
    right.write(rightPos);
    delay(MOVEMENT_DELAY);
  }
}

void flipLeft() {
  for (leftPos = LEFT_START; leftPos >= LEFT_END; leftPos -= INC) {
    left.write(leftPos);
    delay(MOVEMENT_DELAY);
  }
}

void releaseLeft() {
  for (leftPos = LEFT_END; leftPos <= LEFT_START; leftPos += INC) {
    // in steps of 1 degree
    left.write(leftPos);
    delay(MOVEMENT_DELAY);
  }
}

void setup() {
  right.attach(RIGHT_SERVO_PIN);
  left.attach(LEFT_SERVO_PIN);
  Serial.begin(115200);
}

void loop() {
  if (Serial.available() > 0) {
    char c = Serial.read(); // read the next char received
    if (c == '0') {
      flipRight();
    } else if (c == '1') {
      releaseRight();
    } else if (c == '2') {
      flipLeft();
    } else if (c == '3') {
      releaseLeft();
    }
  }
}

