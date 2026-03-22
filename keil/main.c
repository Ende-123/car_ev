/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2026 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "tim.h"
#include "usart.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "motor.h"
#include "string.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
// ??:??????(0=??,1=????)
#define JOYSTICK_CTRL 3
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
volatile uint8_t steer_flag = 2;	// 2=??,0=??,1=??,3=????
uint8_t receive_buf[16] = {0};   
uint8_t receive_len = 0;         
uint8_t receive_frame_start = 0; 
// ??:?????????
int8_t joy_motor1 = 0;
int8_t joy_motor2 = 0;
int8_t joy_motor3 = 0;
int8_t joy_motor4 = 0;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if (GPIO_Pin == GPIO_PIN_12) { 
        uint8_t pa12_level = HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_12);
        if (pa12_level == GPIO_PIN_SET) {
            steer_flag = 1;
        }else{
            steer_flag = 0;
        }
    }
}
/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */
uint8_t X1=0;
uint8_t X2=0;
uint8_t X3=0;
uint8_t X4=0;
int8_t MOTOR1_Speed=0;
int8_t MOTOR2_Speed=0;
int8_t MOTOR3_Speed=0;
int8_t MOTOR4_Speed=0;
	
  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_TIM3_Init();
  MX_TIM4_Init();
  MX_TIM1_Init();
  MX_TIM9_Init();
  MX_USART2_UART_Init();
  /* USER CODE BEGIN 2 */
HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);   
HAL_TIM_PWM_Start(&htim4, TIM_CHANNEL_1);   
HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_3);   
HAL_TIM_PWM_Start(&htim9, TIM_CHANNEL_1);   

MOTOR_Init();

// ????????
HAL_UART_Receive_IT(&huart2, receive_buf, 1);
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    switch(steer_flag){
        // ????:??
        case 0:{
            Motor1_SetSpeed(0);
            Motor3_SetSpeed(0);
            Motor2_SetSpeed(0);
            Motor4_SetSpeed(0);
            HAL_Delay(10);

            Motor2_SetSpeed(10);
            Motor4_SetSpeed(10);
            Motor1_SetSpeed(40);
            Motor3_SetSpeed(40);
            
            while (1)
            {
                X2 = HAL_GPIO_ReadPin(X2_GPIO_Port, X2_Pin);
                X3 = HAL_GPIO_ReadPin(X3_GPIO_Port, X3_Pin);
               
                if (X2 == 1 || X3 == 1 ||  steer_flag != 0)
                {
                    break;
                }
            }
            steer_flag=2; // ????
            break;
        }

        // ????:??
        case 1:{
            Motor1_SetSpeed(0);
            Motor3_SetSpeed(0);
            Motor2_SetSpeed(0);
            Motor4_SetSpeed(0);
            HAL_Delay(10);

            Motor1_SetSpeed(10);
            Motor3_SetSpeed(10);
            Motor2_SetSpeed(40);  
            Motor4_SetSpeed(40);
            
            while (1)
            {
                X2 = HAL_GPIO_ReadPin(X2_GPIO_Port, X2_Pin);
                X3 = HAL_GPIO_ReadPin(X3_GPIO_Port, X3_Pin);
                
                if (X2==1||X3==1  || steer_flag != 1)
                {
                    break; 
                }
            }
            steer_flag=2; // ????
            break;
        }

        // ????(??)
        case 2:{
            X1 = HAL_GPIO_ReadPin(X1_GPIO_Port, X1_Pin);
            X2 = HAL_GPIO_ReadPin(X2_GPIO_Port, X2_Pin);
            X3 = HAL_GPIO_ReadPin(X3_GPIO_Port, X3_Pin);
            X4 = HAL_GPIO_ReadPin(X4_GPIO_Port, X4_Pin);

            if (X1 == 0 && X2 == 0 && X3 == 1 && X4 == 1)
            {
                while (1)
                {
                    Motor1_SetSpeed(10);
                    Motor3_SetSpeed(10);
                    Motor2_SetSpeed(40);
                    Motor4_SetSpeed(40);

                    X2 = HAL_GPIO_ReadPin(X2_GPIO_Port, X2_Pin);
                    X3 = HAL_GPIO_ReadPin(X3_GPIO_Port, X3_Pin);
                    if (X2 == 1 || X3 == 1 ||  steer_flag != 2)
                    {
                        break;
                    }
                }
            }
            else if (X1 == 1 && X2 == 1 && X3 == 0 && X4 == 0)
            {
                while (1)
                {
                    Motor2_SetSpeed(10);
                    Motor4_SetSpeed(10);
                    Motor1_SetSpeed(40);
                    Motor3_SetSpeed(40);

                    X2 = HAL_GPIO_ReadPin(X2_GPIO_Port, X2_Pin);
                    X3 = HAL_GPIO_ReadPin(X3_GPIO_Port, X3_Pin);
                    if (X2 == 1 || X3 == 1  || steer_flag != 2)
                    {
                        break;
                    }
                }
            }
            else
            {
                MOTOR1_Speed = X1 * 20 + X2 * 15 - X3 * 15 - X4 * 20 + 40;
                MOTOR3_Speed = X1 * 20 + X2 * 15 - X3 * 15 - X4 * 20 + 40;
                MOTOR2_Speed = -X1 * 20 - X2 * 15 + X3 * 15 + X4 * 20 + 40;
                MOTOR4_Speed = -X1 * 20 - X2 * 15 + X3 * 15 + X4 * 20 + 40;

                Motor1_SetSpeed(MOTOR1_Speed);
                Motor3_SetSpeed(MOTOR3_Speed);
                Motor2_SetSpeed(MOTOR2_Speed);
                Motor4_SetSpeed(MOTOR4_Speed);
            }
            break;
        }

        // ??:??????(??/??)
        case 3:{
            // ?????????????
            Motor1_SetSpeed(joy_motor1);
            Motor2_SetSpeed(joy_motor2);
            Motor3_SetSpeed(joy_motor3);
            Motor4_SetSpeed(joy_motor4);
            HAL_Delay(20); // ??????,??CPU??
            break;
        }
    }
  }
  /* USER CODE END WHILE */

  /* USER CODE BEGIN 3 */
}
/* USER CODE END 3 */

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLM = 8;
  RCC_OscInitStruct.PLL.PLLN = 168;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = 4;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV4;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance == USART2)
    {
        uint8_t recv_byte = receive_buf[0]; 
        
        // ????#
        if (receive_frame_start == 0)
        {
            if (recv_byte == '#') 
            {
                receive_frame_start = 1;  
                receive_len = 0;          
                memset(receive_buf, 0, sizeof(receive_buf)); 
            }
        }
        // ????;,????
        else
        {
            if (recv_byte == ';')
            {
                if (receive_len == 1)
                {
                    // ??????
                    switch (receive_buf[0])
                    {
                        // ??:??steer_flag=0,????
                        case 'L':
                        case 'l':
                            steer_flag = 0; 
                            HAL_UART_Transmit(&huart2, (uint8_t*)"OK:Left\r\n", 9, 100);
                            break;
                        // ??:??steer_flag=1,????
                        case 'R':
                        case 'r':
                            steer_flag = 1; 
                            HAL_UART_Transmit(&huart2, (uint8_t*)"OK:Right\r\n", 10, 100);
                            break;
                        // ??:????????,????????
                        case 'F':
                        case 'f':
                            steer_flag = 3;
                            joy_motor1 = 40; // ????
                            joy_motor2 = 40; // ????
                            joy_motor3 = 40; // ????
                            joy_motor4 = 40; // ????
                            HAL_UART_Transmit(&huart2, (uint8_t*)"OK:Forward\r\n", 12, 100);
                            break;
                        // ??:????????,????????
                        case 'B':
                        case 'b':
                            steer_flag = 3;
                            joy_motor1 = -40; // ??=??(??)
                            joy_motor2 = -40;
                            joy_motor3 = -40;
                            joy_motor4 = -40;
                            HAL_UART_Transmit(&huart2, (uint8_t*)"OK:Backward\r\n", 13, 100);
                            break;
                        // ??/??:??????
                        case 'S':
                        case 's':
                            steer_flag = 2;
                            // ????
                            joy_motor1 = 0;
                            joy_motor2 = 0;
                            joy_motor3 = 0;
                            joy_motor4 = 0;
                            Motor1_SetSpeed(0);
                            Motor2_SetSpeed(0);
                            Motor3_SetSpeed(0);
                            Motor4_SetSpeed(0);
                            HAL_UART_Transmit(&huart2, (uint8_t*)"OK:Track\r\n", 10, 100);
                            break;
                        default:
                            HAL_UART_Transmit(&huart2, (uint8_t*)"Err:Cmd\r\n", 9, 100);
                            break;
                    }
                }
                else
                {
                    HAL_UART_Transmit(&huart2, (uint8_t*)"Err:Len\r\n", 9, 100);
                }

                // ???????
                receive_frame_start = 0;
                receive_len = 0;
                memset(receive_buf, 0, sizeof(receive_buf));
            }
            // ????,?????
            else if (receive_len < 15)
            {
                receive_buf[receive_len++] = recv_byte;
            }
            // ????,??
            else
            {
                receive_frame_start = 0;
                receive_len = 0;
                memset(receive_buf, 0, sizeof(receive_buf));
            }
        }

        // ??????,????(??!???????)
        __HAL_UART_CLEAR_FLAG(&huart2, UART_FLAG_RXNE);
        HAL_UART_Receive_IT(&huart2, &receive_buf[receive_len], 1);
    }
}
/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */