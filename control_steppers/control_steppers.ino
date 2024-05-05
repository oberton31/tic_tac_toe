#include <AccelStepper.h>
#include <ezButton.h>
#include <Servo.h>


#define EN 8
#define X_DIR 5
#define X_STP 2
#define X_LIMIT 9

#define Y_DIR 6
#define Y_STP 3
#define Y_LIMIT 10

#define Z_SERVO_PIN 11

#define STEP_MM 5


AccelStepper x_stepper(1, X_STP, X_DIR);
AccelStepper y_stepper(1, Y_STP, Y_DIR);
ezButton x_limit(9);
ezButton y_limit(10);

Servo z_servo;

int x_pos = 0;
int y_pos = 0;
bool is_stopped = false;

void home();
void to_position(int x, int y);
void to_out_of_reach_pos();
void lower_pen();
void raise_pen();
void draw(int start_x, int start_y, int end_x, int end_y);
void draw_ttt_board();
void draw__move(int position);
void draw_x(int x, int y);

void setup() {
  Serial.begin(9600);

  pinMode(EN, OUTPUT);
  digitalWrite(EN, LOW);

  x_limit.setDebounceTime(50);
  y_limit.setDebounceTime(50);

  x_stepper.setMaxSpeed(500);
  x_stepper.setAcceleration(100);

  y_stepper.setMaxSpeed(500);
  y_stepper.setAcceleration(100);

  z_servo.attach(Z_SERVO_PIN);

  home();
  draw_ttt_board();
  draw_move(2);
}


void loop() {
  // put your main code here, to run repeatedly:

}

void home() {
  raise_pen();
  x_stepper.setSpeed(-100);
  y_stepper.setSpeed(-100);
  bool x_lim_reached = false;
  bool y_lim_reached = false; 
  while (true) {
    x_limit.loop();
    y_limit.loop();
    if (x_limit.isPressed()) {
      Serial.println("x_limit_reached");
      x_stepper.setCurrentPosition(0);
      x_lim_reached = true;
    } else if (!x_lim_reached) {
      x_stepper.runSpeed();
    }

    if (y_limit.isPressed()) {
      Serial.println("y_limit_reached");
      y_stepper.setCurrentPosition(0);
      y_lim_reached = true;
    } else if (!y_lim_reached) {
      y_stepper.runSpeed();
    }
    if (x_lim_reached & y_lim_reached) {
      return;
    }
  }
  to_position(10, 10);
}


void draw(int start_x, int start_y, int end_x, int end_y) {
  raise_pen();
  to_position(start_x, start_y);
  lower_pen();
  to_position(end_x, end_y);
  raise_pen();
}

void to_position(int x, int y) {
  long x_steps = x * STEP_MM;
  long y_steps = y * STEP_MM;
  x_stepper.setSpeed(200);
  y_stepper.setSpeed(200);
  x_stepper.moveTo(x_steps);
  y_stepper.moveTo(y_steps);
  bool x_reached_pos = false;
  bool y_reached_pos = false;
  while (true) {
    if (x_stepper.distanceToGo() == 0) {
      x_pos = x;
      x_reached_pos = true;
    } else if (!x_reached_pos) {
      x_stepper.run();
    }
    //Serial.println((y_stepper.currentPosition()));
    if (y_stepper.distanceToGo() == 0) {
      y_pos = y;
      y_reached_pos = true;
    } else if (!y_reached_pos) {
      y_stepper.run();
    }
    if (x_reached_pos & y_reached_pos) {
      return;
    }
  }
}

void draw_x(int x, int y) {
  draw(x - 5, y - 5, x + 5, y + 5);
  draw(x - 5, y + 5, x + 5, y - 5);

}

void draw_move(int position) {
  if (position == 0) {
    draw_x(90, 110);
  } else if (position == 1) {
    draw_x(110, 110);
  } else if (position == 2) {
    draw_x(130, 110);
  } else if (position == 3) {
    draw_x(90, 90);
  } else if (position == 4) {
    draw_x(110, 90);
  } else if (position == 5) {
    draw_x(130, 90);
  } else if (position == 6) {
    draw_x(90, 70);
  } else if (position == 7) {
    draw_x(110, 70);
  } else if (position == 8) {
    draw_x(130, 70);
  }
}

void draw_ttt_board() {
  draw(100, 60, 100, 120);
  draw(120, 120, 120, 60);
  draw(80, 80, 140, 80);
  draw(140, 100, 80, 100);
}

void to_out_of_reach_pos() {
  to_position(110, 200);
}

void raise_pen() {
  z_servo.write(70);
  delay(500);
}

void lower_pen() {
  z_servo.write(0);
  delay(500);
}

