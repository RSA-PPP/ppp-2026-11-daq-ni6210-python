// ====================================================================
// PLANCHA METÁLICA DE BLINDAJE / JAULA DE FARADAY (RSA - OpenSCAD)
// ====================================================================
// Genera placa base metálica o cubierta de blindaje para corte láser
// en JLCPCB Sheet Metal (Aluminio / Cobre / Acero de 1.0mm o 2.0mm).

// --------------------------------------------------------------------
// 1. PARÁMETROS DE LA PLANCHA METÁLICA (en mm)
// --------------------------------------------------------------------
plancha_x            = 207.4;  // Largo de la plancha (ajustado al PCB)
plancha_y            = 162.0;   // Ancho de la plancha (ajustado al PCB)
espesor_chapa        = 2.0;    // Espesor de chapa: 1.0mm o 2.0mm (Aluminio/Acero)
radio_esquinas       = 3.0;    // Redondeo de esquinas de la chapa

// --------------------------------------------------------------------
// 2. TALADROS MECÁNICOS Y DE PUESTA A TIERRA (GND)
// --------------------------------------------------------------------
margen_taladros_x    = 4.0;    // Distancia del borde a taladros en X
margen_taladros_y    = 4.0;    // Distancia del borde a taladros en Y
diametro_tornillo_m3 = 3.2;    // Taladro para tornillos M3 (3.2mm libre)
taladro_tierra_gnd   = 4.2;    // Taladro M4 para perno de puesta a tierra / ojillo

// --------------------------------------------------------------------
// 3. MODO DE SALIDA
// --------------------------------------------------------------------
// "3d" = Sólido 3D para exportar a STEP / STL
// "2d" = Proyección plana 2D para exportar a DXF de corte láser
modo_salida          = "3d";

$fn = 40;

module plancha_metalica_2d() {
    difference() {
        // Base rectangular con esquinas redondeadas
        rounded_square([plancha_x, plancha_y], r=radio_esquinas);

        // 4 Taladros de esquinas para postes / separadores M3
        dx = (plancha_x / 2) - margen_taladros_x;
        dy = (plancha_y / 2) - margen_taladros_y;
        for (pos = [[dx, dy], [-dx, dy], [dx, -dy], [-dx, -dy]]) {
            translate([pos[0], pos[1]])
                circle(d=diametro_tornillo_m3);
        }

        // Taladro M4 para terminal de puesta a tierra (GND / Chassis Earth)
        translate([dx - 10, dy - 10])
            circle(d=taladro_tierra_gnd);
    }
}

module rounded_square(size, r=3.0) {
    x = size[0]; y = size[1];
    translate([-x/2, -y/2])
    hull() {
        translate([r, r]) circle(r=r);
        translate([x-r, r]) circle(r=r);
        translate([r, y-r]) circle(r=r);
        translate([x-r, y-r]) circle(r=r);
    }
}

// Renderizado según modo
if (modo_salida == "2d") {
    plancha_metalica_2d();
} else {
    linear_extrude(height=espesor_chapa)
        plancha_metalica_2d();
}
