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

class Thruster {
    public:
        Thruster(PinName pin, float dir);
        void setEvent();
        void clearEvent();
        void set_period(double thruster_time);
        void set_pw(double thruster_pw);
        double get_pw();
        double get_speed();
        void set_max(int new_max);
        int get_max();
        uint32_t thruster_data();
        int set_speed(double pntr);

    protected:
        PwmOut _pwm;
        PinName _pin;
        float _d;
        int _lock;
        int _max;
        double _base_pw, _period;
};
