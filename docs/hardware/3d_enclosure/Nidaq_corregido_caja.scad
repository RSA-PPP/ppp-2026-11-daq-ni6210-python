// ====================================================================
// CARCASA COMPLETA PARAMÉTRICA (RSA - OpenSCAD)
// ====================================================================
// Genera caja de dos piezas (Base + Tapa con postes y tornillos M3).

// --------------------------------------------------------------------
// 1. PARÁMETROS DEL PCB (KiCad)
// --------------------------------------------------------------------
pcb_x             = 207.4;  // Largo de la placa (X)
pcb_y             = 157.0;   // Ancho de la placa (Y)
pcb_grosor        = 1.6;    // Grosor del PCB FR4
altura_postes     = 6.0;    // Distancia del fondo al PCB
altura_comp_max   = 22.0;   // Altura del componente más alto sobre el PCB

// --------------------------------------------------------------------
// 2. PARÁMETROS MECÁNICOS DE LA CAJA
// --------------------------------------------------------------------
pared             = 2.5;    // Grosor de pared
holgura_pcb       = 0.8;    // Holgura en X e Y para holgura de ensamble
radio_esquinas    = 4.0;    // Radio de redondeo exterior
tornillo_dia      = 3.2;    // Orificio pasante M3
inserto_dia       = 4.2;    // Orificio para inserto roscado M3 de latón

// --------------------------------------------------------------------
// 3. MODO DE VISUALIZACIÓN
// --------------------------------------------------------------------
// "ambos" = Base y Tapa separadas para imprimir
// "base"  = Solo la base inferior
// "tapa"  = Solo la tapa superior
// "ensamble" = Vista cerrada montada
modo_vista        = "ambos"; 

$fn = 40;

// Dimensiones interiores
int_x = pcb_x + holgura_pcb * 2;
int_y = pcb_y + holgura_pcb * 2;
ext_x = int_x + pared * 2;
ext_y = int_y + pared * 2;
alt_base = altura_postes + pcb_grosor + 6;
alt_tapa = altura_comp_max + 4;

module cuerpo_base() {
    difference() {
        // Exterior redondeado
        rounded_box([ext_x, ext_y, alt_base], r=radio_esquinas);
        
        // Vaciado interior
        translate([0, 0, pared])
            rounded_box([int_x, int_y, alt_base + 1], r=max(0.5, radio_esquinas - pared));
    }
    
    // 4 Postes de esquinas para sujetar PCB y Tapa
    dx = (int_x / 2) - 4;
    dy = (int_y / 2) - 4;
    for (pos = [[dx, dy], [-dx, dy], [dx, -dy], [-dx, -dy]]) {
        translate([pos[0], pos[1], pared])
        difference() {
            cylinder(d=8.0, h=alt_base - pared);
            // Agujero para tornillo / inserto M3
            cylinder(d=inserto_dia, h=alt_base);
        }
    }
}

module cuerpo_tapa() {
    difference() {
        // Exterior redondeado
        rounded_box([ext_x, ext_y, alt_tapa], r=radio_esquinas);
        
        // Vaciado interior
        translate([0, 0, pared])
            rounded_box([int_x, int_y, alt_tapa + 1], r=max(0.5, radio_esquinas - pared));
            
        // 4 Taladros avellanados para tornillos M3 en esquinas
        dx = (int_x / 2) - 4;
        dy = (int_y / 2) - 4;
        for (pos = [[dx, dy], [-dx, dy], [dx, -dy], [-dx, -dy]]) {
            translate([pos[0], pos[1], -1])
                cylinder(d=tornillo_dia, h=pared + 2);
            translate([pos[0], pos[1], -0.1])
                cylinder(d1=6.5, d2=tornillo_dia, h=2.5); // Avellanado cabeza tornillo
        }
    }
}

module rounded_box(size, r=3.0) {
    x = size[0]; y = size[1]; z = size[2];
    translate([-x/2, -y/2, 0])
    hull() {
        translate([r, r, 0]) cylinder(r=r, h=z);
        translate([x-r, r, 0]) cylinder(r=r, h=z);
        translate([r, y-r, 0]) cylinder(r=r, h=z);
        translate([x-r, y-r, 0]) cylinder(r=r, h=z);
    }
}

// Renderizado según modo
if (modo_vista == "base") {
    cuerpo_base();
} else if (modo_vista == "tapa") {
    cuerpo_tapa();
} else if (modo_vista == "ensamble") {
    cuerpo_base();
    translate([0, 0, alt_base + alt_tapa])
        rotate([180, 0, 0])
            color("lightblue", 0.6) cuerpo_tapa();
} else { // "ambos" lado a lado para imprimir
    translate([-ext_x/2 - 10, 0, 0]) cuerpo_base();
    translate([ext_x/2 + 10, 0, 0]) cuerpo_tapa();
}
