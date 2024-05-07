#include <AccelStepper.h>
#include <ezButton.h>
#include <Servo.h>
#include <string.h>


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
void draw_win(int win_type);
void serialFlush();
void start();

void setup() {
  Serial.begin(9600);

  pinMode(EN, OUTPUT);
  digitalWrite(EN, LOW);

  x_limit.setDebounceTime(50);
  y_limit.setDebounceTime(50);

  x_stepper.setMaxSpeed(500);
  x_stepper.setAcceleration(30);

  y_stepper.setMaxSpeed(500);
  y_stepper.setAcceleration(30);

  z_servo.attach(Z_SERVO_PIN);

  
  serialFlush();
  start();
}


void loop() {
  if (Serial.available() > 0) {
    String msg = Serial.readStringUntil('\n');
    msg.trim();
    if (msg == "start") {
      draw_ttt_board();
    } else if (msg == "return") {
      to_out_of_reach_pos();
    } else {
      String action = msg.substring(0, 3);
      int num = msg.substring(4).toInt();
      if (action == "win") {
        draw_win(num);
        serialFlush();
      } else if (action == "mov") {
        draw_move(num);
      }
    }
    Serial.println("done");
  }
}

void start() {
  while (true) {
    Serial.println("ready");
    delay(500);
    if (Serial.available() > 0) {
      String msg = Serial.readStringUntil('\n');
      //home();
      //to_out_of_reach_pos();
      if (msg == "ready") {
        home();
        to_out_of_reach_pos();
        return;
      }
    }
  }
}

void serialFlush() {
  while(Serial.available() > 0) {
    char remove = Serial.read();
  }
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

void draw_win(int win_type) {
  if (win_type >= 0 & win_type < 3) {
    draw(80, 110 - (win_type * 20), 140, 110 - (win_type * 20)); // row win
  } else if (win_type >= 3 & win_type < 6) {
    draw(90 + (20 * (win_type - 3)), 60, 90 + (20 *(win_type - 3)), 120); // column win
  } else if (win_type == 6) {
    draw(140, 60, 80, 120);
  } else if (win_type == 7) {
    draw(80, 60, 140, 120);
  }
  to_out_of_reach_pos();
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
