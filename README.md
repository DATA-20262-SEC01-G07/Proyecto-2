# IA y desempleo en Estados Unidos: ¿reemplazo u optimización?

Proyecto 2 de Aplicaciones en Ciencia de Datos (DATA-1002), grupos 6 y 7,  Universidad de los Andes, 2026-2.

En este proyecto miramos qué ha pasado con el desempleo en Estados Unidos desde 2021 y si tiene relación con qué tan expuesta está cada ocupación a la inteligencia artificial. También revisamos si el nivel educativo y el tiempo que las personas llevan buscando trabajo cambian esa relación.

Trabajamos con datos de Estados Unidos porque la información es mucho más completa. En Colombia todavía hay muy pocos datos sobre el uso de la IA y su efecto en el empleo. Por eso usamos el caso de Estados Unidos como una alerta temprana para pensar qué podría pasar aquí y cómo prepararnos desde la educación.

## Pregunta analítica

¿Cómo se relacionan el nivel educativo y el tiempo que tardan en reemplearse los trabajadores desempleados con la exposición a la inteligencia artificial en Estados Unidos desde 2021, y qué ocupaciones altamente expuestas han visto subir su desempleo frente a las que lo mantuvieron estable entre 2021 y 2026, junto con las características que distinguen a cada grupo?

La dividimos en dos partes:

- **Parte A:** cómo se relacionan el nivel educativo y el tiempo buscando empleo con la exposición a la IA.
- **Parte B:** qué ocupaciones muy expuestas subieron su desempleo, cuáles lo mantuvieron estable y qué las diferencia.

El "tiempo para reemplearse" lo medimos como las semanas que la persona desempleada lleva buscando trabajo al momento de la encuesta.

## Hipótesis

El aumento reciente del desempleo en Estados Unidos está relacionado con el auge de la inteligencia artificial: entre más expuesta a la IA esté una ocupación, más ha crecido su desempleo. Además, esta relación es más fuerte en los trabajadores con menor nivel educativo.

## Objetivos

**General:** analizar cómo se relacionan la exposición a la IA, el nivel educativo y el tiempo que los desempleados tardan en volver a trabajar en Estados Unidos (2021–2026), para identificar qué ocupaciones muestran señales de reemplazo u optimización y sacar lecciones que ayuden a Colombia a preparar a su población desde la educación.

**Específicos:**

1. Unir la encuesta CPS con el índice de exposición a la IA, la lista de ocupaciones del Censo y los datos de empleo y salarios del BLS, revisando que en el cruce no se pierdan ni se dupliquen registros.
2. Clasificar las ocupaciones en tres niveles de exposición a la IA (baja, media y alta), usando la exposición evaluada por humanos del estudio de Eloundou et al. (2023).
3. Comparar las semanas que llevan buscando empleo los desempleados según la exposición a la IA de su último oficio y su nivel educativo.
4. Identificar qué ocupaciones muy expuestas aumentaron su tasa de desempleo, cuáles la mantuvieron estable y cuáles la redujeron, comparando 2022–2023 con 2025–2026.
5. Describir qué distingue a cada grupo: salario mediano, nivel educativo, edad, sexo y grupo ocupacional.
6. Proponer recomendaciones educativas para Colombia y una forma de repetir el estudio con datos colombianos.

## Contexto

Desde que salió ChatGPT en noviembre de 2022, la IA generativa empezó a usarse todos los días en tareas como escribir, programar, traducir o analizar información. Con eso apareció la duda de si la IA va a quitar empleos o si más bien va a ayudar a la gente a trabajar mejor.

En 2023, investigadores de OpenAI y de la Universidad de Pensilvania calcularon qué tan expuesta está cada ocupación a estos modelos. Que una tarea esté expuesta no quiere decir que la persona vaya a perder su trabajo: la IA puede reemplazarla, pero también puede ayudarle a ser más productiva. Eso es justamente lo que queremos revisar con datos reales de desempleo.

Para Colombia el tema importa mucho. El país ya tiene problemas de desempleo e informalidad, y no todo el mundo ha tenido acceso a formación en tecnología. Si la IA empieza a afectar el empleo, los primeros perjudicados serían quienes tienen menos oportunidades de aprender a usarla.

## ¿Para qué sirve?

Aunque los datos son de Estados Unidos, la idea es aprovechar esa experiencia para Colombia. Lo que encontremos allá nos dice qué tipo de trabajadores y qué niveles educativos podrían verse más afectados si pasa lo mismo aquí.

Con esa información, entidades como el Ministerio de Educación o el SENA podrían adelantarse y empezar a enseñar a usar la IA como herramienta, antes de que el problema llegue.

## Datos

| Fuente | Qué usamos | Cada fila es | Período |
|---|---|---|---|
| [CPS – Current Population Survey](https://cps.ipums.org/cps/) (U.S. Census Bureau y BLS, descargada desde IPUMS-CPS) | Situación laboral, semanas desempleado, nivel educativo, edad, sexo, ocupación y peso de muestreo | Una persona encuestada en un mes | Enero 2021 – octubre 2026 |
| [Lista de ocupaciones del Censo 2018](https://www.census.gov/topics/employment/industry-occupation/guidance/code-lists.html) | Equivalencia entre el código de ocupación del CPS y el código SOC | Una ocupación del Censo | 2018 |
| [BLS OEWS](https://www.bls.gov/oes/tables.htm) (Occupational Employment and Wage Statistics) | Empleo total y salario mediano anual de cada ocupación | Una ocupación (código SOC) | [año] |
| [Índice de exposición a la IA](https://github.com/openai/GPTs-are-GPTs) (Eloundou et al., 2023) | Exposición de las tareas de cada ocupación a la IA | Una ocupación (código O*NET-SOC) | 2023 |

### Cómo conseguir el archivo del CPS

El archivo del CPS (`cps_00001.csv`) no está en el repositorio porque pesa demasiado. Para obtenerlo:

1. Abrir este link https://drive.google.com/drive/folders/1RJNNGGCqOdKzEQ4liJFgQYuejrqTWWYS?usp=drive_link

2. Descomprimir el archivo y guardarlo en `data/raw`

## Preparación de los datos

Estas son las decisiones más importantes que tomamos:

- Nos quedamos solo con las personas que hacen parte de la fuerza laboral (empleadas o desempleadas) y que tienen una ocupación registrada.
- Calculamos las tasas de desempleo con los pesos de muestreo del CPS, porque cada persona encuestada representa a miles de personas.
- Tomamos 2022 como año de referencia, porque fue cuando la economía salió de la pandemia.
- Dividimos las ocupaciones en tres grupos del mismo tamaño (terciles) según su exposición a la IA: baja, media y alta.
- Dijimos que el desempleo de una ocupación "subió" o "bajó" si cambió en más de 1 punto entre 2022–2023 y 2025–2026. Si cambió menos, lo contamos como "estable".
- Dejamos por fuera las ocupaciones con menos de 30 desempleados en la comparación y con menos de 100 en el ranking, porque en ocupaciones tan pequeñas la tasa cambia demasiado con una sola persona.

## Estructura del repositorio

```
Proyecto-2/
├── README.md
├── requirements.txt
├── data/
│   └── raw/
│       ├── cps_00001.csv            (No está en el repositorio, ver "Cómo conseguir el archivo del CPS")
│       ├── census_crosswalk.csv
│       ├── bls_oews_national.csv
│       └── occ_level.csv
└── notebooks/
    └── cargads.ipynb
```

## Cómo correr el proyecto

1. Clonar el repositorio:

   ```
   git clone https://github.com/DATA-20262-SEC01-G07/Proyecto-2.git
   ```

2. Instalar las librerías (recomendamos hacerlo en un ambiente virtual):

   ```
   pip install -r requirements.txt
   ```

3. Descargar el archivo del CPS y guardarlo en `data/raw/`.

4. Abrir `notebooks/cargads.ipynb` y correr las celdas de arriba hacia abajo.

## Resultados
Entre 2022 y 2026 la tasa de desempleo pasó de 2,24 % a 2,95 % en las ocupaciones de exposición alta, de 5,09 % a 5,65 % en las de exposición baja y de 3,38 % a 3,52 % en las de exposición media. Respecto a 2022, el desempleo de la exposición alta creció 31,6 %, el de la baja 11,1 % y el de la media 4,1 %, pero la exposición alta parte del nivel más bajo (+0,71 puntos, frente a +0,56 en la baja). De las 15 ocupaciones con mayor tasa de desempleo, solo una es de exposición alta.

Comparando 2022–2023 con 2025–2026, el desempleo subió más de un punto en el 42 % de las ocupaciones de exposición alta, frente al 32 % en las de exposición baja y el 33 % en las de exposición media. La correlación entre exposición y cambio en la tasa es de 0,12. Dentro de las de exposición alta, las que subieron (42) tienen mayor exposición mediana (0,55 frente a 0,50), menos empleo total (188.695 frente a 295.650), salarios similares y la misma tasa previa. Son más del grupo Management, Business, Science, and Arts (69,0 % frente a 58,8 %) y sus trabajadores tienen más pregrado o más (72,0 % frente a 56,7 %) y menos mujeres (41,8 % frente a 52,9 %).

El 22,3 % de los desempleados lleva 27 semanas o más buscando trabajo. Este porcentaje sube con la edad (14,7 % entre los 16 y 24 años, 27,5 % entre los 55 y 64) y es mayor en la exposición alta (25,8 %) que en la baja y media (21,0 % y 21,4 %). También aumenta con el nivel educativo, de 18,5 % con menos de secundaria a 25,4 % con posgrado.

Al cruzar educación y exposición, el desempleo de larga duración es mayor en la exposición alta que en la baja en todos los niveles educativos, pero la diferencia varía. Es pequeña en secundaria (22,5 % frente a 21,7 %) y en pregrado (27,2 % frente a 25,3 %), y grande en técnico o asociado (27,6 % frente a 20,6 %) y en posgrado (28,7 % frente a 21,3 %). En la exposición alta el porcentaje va de 22,0 % con menos de secundaria a 28,7 % con posgrado, mientras que en la baja no sigue una tendencia clara (el valor más alto es 25,3 % en pregrado) y en la media va de 17,3 % a 23,3 %.

Hay un apoyo débil a que el desempleo haya crecido más donde la exposición es mayor. La hipótesis de que la relación es más fuerte con menor educación no se evaluó con el cambio en el desempleo, y en la duración ocurre lo contrario: la diferencia entre exposición alta y baja es mayor en los niveles educativos más altos. Los resultados son asociaciones y no permiten atribuir el desempleo a la IA.

Los resultados responden la pregunta analítica de la siguiente manera. El desempleo de larga duración (27 semanas o más) aumenta con el nivel educativo (de 18,5 % con menos de secundaria a 25,4 % con posgrado) y es mayor en la exposición alta (25,8 %) que en la baja y media (21,0 % y 21,4 %). La diferencia entre exposición alta y baja es mayor en técnico o asociado (27,6 % frente a 20,6 %) y en posgrado (28,7 % frente a 21,3 %). Esta duración es el tiempo que llevan buscando empleo al momento de la encuesta y no el tiempo hasta reemplearse. En cuanto a las ocupaciones, el desempleo subió más de un punto en el 42 % de las de exposición alta. Las que subieron tienen mayor exposición mediana (0,55 frente a 0,50), menos empleo total, más presencia del grupo Management, Business, Science, and Arts (69,0 % frente a 58,8 %), más trabajadores con pregrado o más (72,0 % frente a 56,7 %) y menos mujeres (41,8 % frente a 52,9 %). Estas son asociaciones y no prueban que la IA cause el desempleo.

## Limitaciones

- **Estar expuesto no es lo mismo que ser reemplazado.** El índice mide lo que la IA podría hacer en cada ocupación, no si las empresas la están usando.
- **No podemos decir que la IA cause el desempleo.** En los mismos años subieron las tasas de interés, hubo despidos grandes en empresas de tecnología y la economía se estaba recuperando de la pandemia.
- **El cruce de ocupaciones no es perfecto.** Al traducir los códigos se juntan oficios distintos, y algunas ocupaciones (las "all other" y las militares) quedan sin dato de exposición.
- **Los resultados son de Estados Unidos** y no se pueden pasar tal cual a Colombia.
- **El período "antes" (2022–2023) ya incluye meses en los que existía ChatGPT**, así que no es un antes y después exacto.
- **En ocupaciones pequeñas la tasa es inestable.** Por eso pusimos mínimos de desempleados, pero esos cortes los decidimos nosotros.
- **2026 solo tiene datos hasta octubre**, mientras que los otros años tienen los doce meses.

## Siguientes pasos

A partir de esto, se proponen las siguientes acciones. La primera es un programa de reubicación y recapacitación para trabajadores con formación técnica, de pregrado o de posgrado en ocupaciones de exposición alta, que son quienes tienen mayor desempleo de larga duración, con formación en habilidades complementarias a la IA y orientación hacia ocupaciones de menor exposición. La segunda es una campaña de reempleo para personas de 55 a 64 años, entre quienes el 27,5 % de los desempleados lleva 27 semanas o más buscando trabajo, frente al 14,7 % entre los 16 y 24 años. La tercera es monitorear periódicamente las ocupaciones de exposición alta del grupo Management, Business, Science, and Arts con poco empleo total, que son las que más suben, para actuar antes de que el desempleo se prolongue. La cuarta es no limitar las políticas a la exposición alta, porque las ocupaciones de exposición baja tienen la mayor tasa de desempleo (5,65 % en 2026 frente a 2,95 % en las altas).

Para fortalecer estas conclusiones, falta estimar modelos que controlen por edad, sexo y grupo ocupacional, y seguir a las mismas personas entre meses de la CPS para medir el tiempo hasta reemplearse. Una vez completado este análisis para Estados Unidos, el equipo quiere hacer un estudio similar para Colombia con la GEIH del DANE, usando una equivalencia entre la CIUO-08 A.C. y la clasificación SOC de Estados Unidos para adaptar el índice de exposición.

## Equipo

- Ana Sofía Ángulo
- Juliana Hernández Hernández
- María Gabriela Martín Avila
- Tomás Pulgarín Castañeda

## Referencias

- Eloundou, T., Manning, S., Mishkin, P. y Rock, D. (2023). *GPTs are GPTs: An Early Look at the Labor Market Impact Potential of Large Language Models.*
- IPUMS CPS. [Copiar aquí la cita exacta que IPUMS muestra al descargar el extracto.]
- U.S. Census Bureau. *2018 Census Occupation Code List.*
- U.S. Bureau of Labor Statistics. *Occupational Employment and Wage Statistics (OEWS).*