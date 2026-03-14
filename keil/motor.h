#ifndef _Motor_h_
#define _Motor_h_

#include "main.h"
#include "tim.h"
#include "gpio.h"


void MOTOR_Init(void);
void Motor1_SetSpeed(int8_t Speed);

void Motor2_SetSpeed(int8_t Speed);
void Motor3_SetSpeed(int8_t Speed);

void Motor4_SetSpeed(int8_t Speed);


#endif