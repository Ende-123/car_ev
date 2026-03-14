#include "Motor.h"



void MOTOR_Init(void){
HAL_TIM_PWM_Start(&htim1,TIM_CHANNEL_1);
HAL_TIM_PWM_Start(&htim4,TIM_CHANNEL_1);
HAL_TIM_PWM_Start(&htim9,TIM_CHANNEL_1);
HAL_TIM_PWM_Start(&htim3,TIM_CHANNEL_1);
	
	
HAL_GPIO_WritePin(GPIOC, GPIO_PIN_7, GPIO_PIN_RESET); 
HAL_GPIO_WritePin(GPIOD, GPIO_PIN_13, GPIO_PIN_RESET); 
HAL_GPIO_WritePin(GPIOE, GPIO_PIN_10, GPIO_PIN_RESET); 
HAL_GPIO_WritePin(GPIOE, GPIO_PIN_6, GPIO_PIN_RESET); 
	

}
void Motor1_SetSpeed(int8_t Speed){
	if(Speed>=0){
	
		HAL_GPIO_WritePin(PA11_GPIO_Port,PA11_Pin,GPIO_PIN_RESET);
	
		__HAL_TIM_SET_COMPARE(&htim1,TIM_CHANNEL_1,Speed);
	}
	else{
			HAL_GPIO_WritePin(PA11_GPIO_Port,PA11_Pin,GPIO_PIN_SET);
	
		__HAL_TIM_SET_COMPARE(&htim1,TIM_CHANNEL_1,-Speed);
	}

}

void Motor2_SetSpeed(int8_t Speed){
	
	if(Speed>=0){	HAL_GPIO_WritePin(PD13_GPIO_Port,PD13_Pin,GPIO_PIN_RESET);
	
		__HAL_TIM_SET_COMPARE(&htim4,TIM_CHANNEL_1,Speed);
	}
	else{
			HAL_GPIO_WritePin(PD13_GPIO_Port,PD13_Pin,GPIO_PIN_SET);
	
		__HAL_TIM_SET_COMPARE(&htim4,TIM_CHANNEL_1,-Speed);
	}
}


void Motor3_SetSpeed(int8_t Speed){
	
	if(Speed>=0){	HAL_GPIO_WritePin(PE6_GPIO_Port,PE6_Pin,GPIO_PIN_RESET);
	
		__HAL_TIM_SET_COMPARE(&htim9,TIM_CHANNEL_1,Speed);
	}
	else{
			HAL_GPIO_WritePin(PE6_GPIO_Port,PE6_Pin,GPIO_PIN_SET);
	
		__HAL_TIM_SET_COMPARE(&htim9,TIM_CHANNEL_1,-Speed);
	}
}


void Motor4_SetSpeed(int8_t Speed){
	
	if(Speed>=0){	HAL_GPIO_WritePin(PA7_GPIO_Port,PA7_Pin,GPIO_PIN_RESET);
	
		__HAL_TIM_SET_COMPARE(&htim3,TIM_CHANNEL_1,Speed);
	}
	else{
			HAL_GPIO_WritePin(PA7_GPIO_Port,PA7_Pin,GPIO_PIN_SET);
	
		__HAL_TIM_SET_COMPARE(&htim3,TIM_CHANNEL_1,-Speed);
	
	}
}

