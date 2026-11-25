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

Pendiente (Lo voy a rellenar cunando Tomás y Juliana terminen)
## Limitaciones

- **Estar expuesto no es lo mismo que ser reemplazado.** El índice mide lo que la IA podría hacer en cada ocupación, no si las empresas la están usando.
- **No podemos decir que la IA cause el desempleo.** En los mismos años subieron las tasas de interés, hubo despidos grandes en empresas de tecnología y la economía se estaba recuperando de la pandemia.
- **El cruce de ocupaciones no es perfecto.** Al traducir los códigos se juntan oficios distintos, y algunas ocupaciones (las "all other" y las militares) quedan sin dato de exposición.
- **Los resultados son de Estados Unidos** y no se pueden pasar tal cual a Colombia.
- **El período "antes" (2022–2023) ya incluye meses en los que existía ChatGPT**, así que no es un antes y después exacto.
- **En ocupaciones pequeñas la tasa es inestable.** Por eso pusimos mínimos de desempleados, pero esos cortes los decidimos nosotros.
- **2026 solo tiene datos hasta octubre**, mientras que los otros años tienen los doce meses.

## Siguientes pasos

Con los resultados obtenidos, los siguientes pasos del proyecto deben apuntar a qué hacer en Colombia con lo que se encontró en Estados Unidos. Como el desempleo creció algo más en las ocupaciones muy expuestas a la IA, y estas son sobre todo profesionales y administrativas, el primer paso es identificar cuáles ocupaciones colombianas se parecen a ellas y qué porcentaje de la fuerza laboral del país las ocupa, usando la GEIH del DANE y una equivalencia entre la clasificación ocupacional colombiana y los códigos SOC. Como la relación entre exposición y desempleo resultó débil y no se puede atribuir a la IA, el segundo paso es no sacar conclusiones fuertes, sino monitorear estas ocupaciones en Colombia a medida que haya más datos sobre el uso real de la IA en las empresas. Como la larga duración del desempleo fue mayor en las personas con más estudios y en las ocupaciones más expuestas, el tercer paso es que el Ministerio de Educación, el SENA y las universidades enseñen el uso de la IA como herramienta, empezando por los programas que forman para esos oficios y sin dirigirla solo a quienes tienen menos escolaridad. Por último, como en Colombia hay mucha informalidad y los datos de Estados Unidos no se pueden trasladar tal cual, conviene repetir el estudio con datos colombianos para comprobar si el patrón se mantiene antes de diseñar políticas concretas.

## Uso de inteligencia artificial

Con autorización del profesor, usamos herramientas de IA como apoyo para [describir: por ejemplo, revisar la redacción del README y revisar el código]. Las decisiones del análisis y la revisión final las hicimos nosotros.

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