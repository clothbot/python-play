// union and difference operators
union() {
    cylinder(r=1,h=10);
    sphere(r=2);
    translate([0,0,10]) sphere(r=2);
}
difference() {
    union() {
        cylinder(r=10,h=2,center=true);
        cylinder(r=9,h=3,center=true);
    }
    cylinder(r=8,h=4,center=true);
}
