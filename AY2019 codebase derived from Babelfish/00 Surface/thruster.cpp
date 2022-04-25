/*
 * Thrust class for LPC1768
 * US Naval Academy
 * Robotics and Control TSD
 * Patrick McCorkell
 *
 * Created: 2020 Nov 23
 * 
 */

#include "mbed.h"
#include "thruster.h"

//Instantiation accepts PWM pin and direction of prop blade
//Direction is -1 or 1.
//1 for normal, -1 if blade reversed.
Thruster::Thruster(PinName pin, float dir) : _pwm(pin), _d(dir) {
    _lock=0;            // emergency lockout, default is 0
    _pin=pin;           // PWM pin
    _base_pw=1.5;       // 1.5ms
    set_pw(_base_pw);   // set PWM to 1.5ms
    _period=2.5;        // 2.5ms
    set_period(_period); // set period to 2.5ms (400Hz)
    _max=150;           // max PWM value in us
    //printf("Thruster: %f\r\n",d);
}

//Sets Event for Emergency Stop and sets lockout to set_speed() function.
void Thruster::setEvent() {
    _lock=1;            // set _lock flag to lockout set_speed functionality.
    set_pw(_base_pw);   // write the neutral PWM value.
}

//Clears Event for Emergency Stop of thruster and removes lockout from set_speed() function.
void Thruster::clearEvent() {
    _lock=0;            // set _lock flag back to 0, enabling set_speed functionality.
}

//Set PWM period in ms.
void Thruster::set_period(double thruster_time) {
    _period=thruster_time;
    _pwm.period(_period/1000);
}

//Set PWM pulsewidth in ms
void Thruster::set_pw(double thruster_pw) {
    double s_pw=(thruster_pw/1000);
    printf("log: set_pw: %f\r\n",s_pw);
    _pwm.pulsewidth(s_pw);
}

//Returns PWM pulsewidth in ms.
double Thruster::get_pw() {
    //read duty cycle times period
    double g_pw = (_pwm.read()*_period);
    //printf(" get_pw: %f, ",g_pw);
    return g_pw;
}

//Returns PWM output relative to 1.5ms.
double Thruster::get_speed() {
    double g_speed = (get_pw()-_base_pw);
    //printf("get_speed: %f, ",g_speed);
    return g_speed;
}

//formats PWM as an 2 uint16_t joined to make uint32_t for serial data streaming
//MSB uint16_t indicates direction, 0 for positive, 1 for negative.
//LSB uint16_t is 10us resolution of PWM
uint32_t Thruster::thruster_data() {
    double speed=get_speed();
    uint32_t dir=0x0;
    uint32_t data=0x0;
    if (speed<0) dir =0x00010000;
    data=static_cast<unsigned int>(abs(int(speed*100000)));
    data=data+dir;
    return data;
}

//Accepts adjustment to max value of pw [x,500] us for set_speed() function.
//Returns 1 if successful.
void Thruster::set_max(int new_max) {
    if (new_max<=500) {
        _max=new_max;
    }
}

int Thruster::get_max() {
    int buffer = _max;
    return buffer;
}

//Accepts adjustment to pw [-500,500] us that is added to 1.5ms.
//Returns 1 if successful.
int Thruster::set_speed(double speed_pw) {
    int returnval = 0;
    if (_lock==1) {
        set_pw(_base_pw);
    }
    else if (abs(speed_pw) > _max) {
        //print("max speed exceeded");
        returnval=0;
    }
    else {
        double tolerance_pw=0.001;
        double target_pw=(_d*speed_pw)+_base_pw;
        double current_pw=get_pw();
        double diff_pw=abs(target_pw-current_pw);
        if (diff_pw>tolerance_pw) {
            set_pw(target_pw);
            returnval = 1;
        }
    }
    return returnval;
}

