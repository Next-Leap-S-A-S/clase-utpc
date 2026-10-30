# El derecho ya cambió, ¿y los abogados?

Taller de Next Leap para la UPTC (Universidad Pedagógica y Tecnológica de Colombia). Dura 2 horas y está dirigido a abogados en ejercicio y estudiantes de posgrado. Es un solo sitio autocontenido que reúne la clase y la biblioteca de prompts.

**Publicado en:** https://next-leap-s-a-s.github.io/clase-utpc/ (la dirección conserva el nombre anterior del repositorio).

## Seis pestañas

1. **El cambio.** Cuatro hechos con su fuente y qué cambió y qué no para el abogado.
2. **Método RCI.** Rol, contexto e instrucción, con un ejemplo antes y después.
3. **Laboratorio.** Cuatro ejercicios y diez prompts con material ficticio. Cada ejercicio enlaza a las subáreas de la Biblioteca con prompts del mismo tipo de tarea.
4. **Biblioteca.** 122 prompts extensos en 11 áreas y 55 subáreas del derecho colombiano, con filtro por área y subárea, buscador, favoritos, campos editables entre corchetes y botón de copiar. El atajo `/` lleva al buscador.
5. **Asistentes.** Tres recetas de asistentes personalizados.
6. **Antes de servir.** Secreto profesional, datos personales, anonimización y lista de verificación de ocho puntos. La lista guarda su estado en el navegador (`localStorage`).

## Marca

Identidad de la UPTC como principal: rojo `#b31b34`, amarillo `#ffcc29` y negro, tomados del CSS de uptc.edu.co porque el manual de identidad no es público. El logotipo es el SVG oficial que usa el portal, recortado y convertido a PNG. Se usa con fines académicos. El logo de Next Leap aparece junto al de la UPTC en la cabecera y en el pie. Tipografías: Inter e IBM Plex Mono.

## Cómo está construido

Un único `index.html` ASCII puro, con tipografías y logos incrustados en base64. No hace peticiones externas y funciona sin conexión.

```
src/
  template.html    marcado, estilos y lógica (UTF-8, legible)
  asistentes.js    los doce asistentes de ejemplo (la página muestra tres)
  prompts-*.js     la biblioteca, un archivo por área
  assets/          tipografías .woff2 y logos de Next Leap y de la UPTC
  build.py         ensambla, revisa y convierte a ASCII
deck/
  el-derecho-ya-cambio-uptc.pptx   presentación de 21 láminas con guion del orador
```

Edite con tildes normales y corra:

```
python3 src/build.py             # avisa y omite los archivos de área que falten
python3 src/build.py --estricto  # exige los 11 archivos, sus nueve campos y al menos 100 prompts
```

Cada prompt de la biblioteca es un objeto `{a, s, t, r, c, i, mal, por, tip}`: área, subárea, título, rol, contexto, instrucción, versión débil del pedido, por qué falla y consejo. Las áreas, en orden: civil, comercial, laboral, penal, administrativo, constitucional, tributario, ambiental, digital, internacional y práctica.

`build.py` revisa que cada asistente tenga entre 300 y 600 palabras, que exija la marca «(por verificar)» y que la prosa de la plantilla, los asistentes y los prompts no tenga guiones largos, punto y coma, signos de exclamación ni las frases y conectores excluidos por la guía de redacción. Si algo falla, lista los problemas y no genera el archivo.

## Rigor jurídico

Todas las citas de norma de los prompts y de los asistentes llevan «(por verificar)». Muchas se escribieron de memoria y deben contrastarse con el texto oficial vigente antes de usarse. La página no cita sentencias por número, salvo la T-323 de 2024, el caso *Mata contra Avianca* y el Acuerdo PCSJA24-12243 de 2024, que se verificaron en fuentes publicadas. La fecha exacta de la T-323 y el artículo del Acuerdo que exige declarar el uso de IA quedan pendientes.

## Manejo de información

Los prompts están pensados para trabajar con información anonimizada y en herramientas aprobadas por la firma o la entidad. La salida es un borrador. La verificación, la decisión y la firma son del abogado responsable.

---

Next Leap para la UPTC
