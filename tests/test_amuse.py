# Test consistency between galpy and amuse
from __future__ import print_function, division
import os
import numpy
import subprocess
from galpy.orbit import Orbit
from galpy import potential
from galpy.util import bovy_conversion,bovy_coords

from galpy.potential import to_amuse

from amuse.lab import *
from amuse.couple import bridge
from amuse.datamodel import Particles

from astropy import units as apy_u

def test_amuse_potential_with_physical():
    ro, vo=8., 220.
    amp= 1e8 / bovy_conversion.mass_in_msol(ro=ro, vo=vo)
    a= 0.8 / ro

    amp_u= 1e8 * apy_u.solMass
    a_u= 0.8 * apy_u.kpc
    ro_u, vo_u= 8.*apy_u.kpc, 220.*apy_u.km/apy_u.s

    x, y, z = 3|units.kpc, 4|units.kpc, 2|units.kpc
    r = 5|units.kpc

    # ------------------------------------
    # get_potential_at_point
    pot1= potential.TwoPowerSphericalPotential(amp=amp, a=a, ro=ro, vo=vo)
    gg1 = pot1(5/ro, 2/ro)
    gg1 = gg1.to_value(apy_u.km**2 / apy_u.s**2) if hasattr(gg1, 'unit') else gg1
    amuse_pot1= to_amuse(pot1)
    ag1= amuse_pot1.get_potential_at_point(0, x, y, z)

    assert numpy.abs(gg1 - ag1.value_in(units.kms**2)) < 1e-10

    pot2= potential.TwoPowerSphericalPotential(amp=amp_u, a=a_u, ro=ro_u, vo=vo_u)
    gg2 = pot1(5*apy_u.kpc, 2*apy_u.kpc)
    gg2 = gg2.to_value(apy_u.km**2 / apy_u.s**2) if hasattr(gg2, 'unit') else gg2
    amuse_pot2= to_amuse(pot2)
    ag2= amuse_pot2.get_potential_at_point(0, x, y, z)

    assert numpy.abs(gg2 - ag2.value_in(units.kms**2)) < 1e-10

    assert numpy.abs(ag1 - ag2) < 1e-10|units.kms**2

    # ------------------------------------
    # test get_gravity_at_point
    pot1= potential.TwoPowerSphericalPotential(amp=amp, a=a, ro=ro, vo=vo)
    amuse_pot1= to_amuse(pot1)
    ax1, ay1, az1= amuse_pot1.get_gravity_at_point(0, x, y, z)

    pot2= potential.TwoPowerSphericalPotential(amp=amp_u, a=a_u, ro=ro_u, vo=vo_u)
    amuse_pot2= to_amuse(pot2)
    ax2, ay2, az2= amuse_pot2.get_gravity_at_point(0, x, y, z)

    assert numpy.abs(ax1 - ax2) < 1e-10|units.kms/units.Myr
    assert numpy.abs(ay1 - ay2) < 1e-10|units.kms/units.Myr
    assert numpy.abs(az1 - az2) < 1e-10|units.kms/units.Myr

    # ------------------------------------
    # test mass_density
    pot1= potential.TwoPowerSphericalPotential(amp=amp, a=a, ro=ro, vo=vo)
    grho1 = pot1.dens(5/ro, 2/ro)
    grho1 = grho1.to_value(apy_u.solMass/apy_u.pc**3) if hasattr(grho1, 'unit') else grho1
    amuse_pot1= to_amuse(pot1)
    arho1= amuse_pot1.mass_density(x, y, z)

    assert numpy.abs(grho1 - arho1.value_in(units.MSun/units.parsec**3)) < 1e-10

    pot2= potential.TwoPowerSphericalPotential(amp=amp_u, a=a_u, ro=ro_u, vo=vo_u)
    grho2= pot2.dens(5*apy_u.kpc, 2*apy_u.kpc)
    grho2= grho2.to_value(apy_u.solMass/apy_u.pc**3) if hasattr(grho2, 'unit') else grho2
    amuse_pot2= to_amuse(pot2)
    arho2= amuse_pot2.mass_density(x, y, z)

    assert numpy.abs(grho2 - arho2.value_in(units.MSun/units.parsec**3)) < 1e-10

    assert numpy.abs(arho1 - arho2) < 1e-10|units.MSun/units.parsec**3

    # ------------------------------------
    # test circular_velocity
    pot1= potential.TwoPowerSphericalPotential(amp=amp, a=a, ro=ro, vo=vo)
    gv1= pot1.vcirc(1*apy_u.kpc)
    gv1=  gv1.to_value(apy_u.km/apy_u.s) if hasattr(gv1, 'unit') else gv1
    amuse_pot1= to_amuse(pot1)
    av1= amuse_pot1.circular_velocity(1|units.kpc)

    assert numpy.abs(gv1 - av1.value_in(units.kms)) < 1e-10

    pot2= potential.TwoPowerSphericalPotential(amp=amp_u, a=a_u, ro=ro_u, vo=vo_u)
    gv2= pot2.vcirc(1*apy_u.kpc)
    gv2=  gv2.to_value(apy_u.km/apy_u.s) if hasattr(gv2, 'unit') else gv2
    amuse_pot2= to_amuse(pot2)
    av2= amuse_pot2.circular_velocity(1|units.kpc)

    assert numpy.abs(gv2 - av2.value_in(units.kms)) < 1e-10

    assert numpy.abs(av1 - av2) < 1e-10|units.kms

    # ------------------------------------
    # test enclosed_mass

    pot1= potential.TwoPowerSphericalPotential(amp=amp, a=a, ro=ro, vo=vo)
    gm1= pot1.mass(1/ro)
    gm1= gm1.to_value(apy_u.solMass) if hasattr(gm1, 'unit') else gm1
    amuse_pot1= to_amuse(pot1)
    am1= amuse_pot1.enclosed_mass(1|units.kpc)

    assert numpy.abs(gm1 - am1.value_in(units.MSun)) < 3e-8

    pot2= potential.TwoPowerSphericalPotential(amp=amp_u, a=a_u, ro=ro_u, vo=vo_u)
    gm2= pot2.mass(1*apy_u.kpc)
    gm2= gm2.to_value(apy_u.solMass) if hasattr(gm2, 'unit') else gm2
    amuse_pot2= to_amuse(pot2)
    am2= amuse_pot2.enclosed_mass(1|units.kpc)

    assert numpy.abs(gm2 - am2.value_in(units.MSun)) < 3e-8

    assert numpy.abs(am1 - am2) < 1e-10|units.MSun

    return None

def test_amuse_MN3ExponentialDiskPotential():
    mn= potential.MN3ExponentialDiskPotential(normalize=1.,hr=0.5,hz=0.1)
    tmax= 3.
    vo,ro= 215., 8.75
    o= Orbit([1.,0.1,1.1,0.3,0.1,0.4],ro=ro,vo=vo)
    run_orbitIntegration_comparison(o,mn,tmax,vo,ro)
    return None

def test_amuse_MiyamotoNagaiPotential():
    mp= potential.MiyamotoNagaiPotential(normalize=1.,a=0.5,b=0.1)
    tmax= 4.
    vo,ro= 220., 8.
    o= Orbit([1.,0.1,1.1,0.3,0.1,0.4],ro=ro,vo=vo)
    run_orbitIntegration_comparison(o,mp,tmax,vo,ro)
    return None

def test_amuse_NFWPotential():
    np= potential.NFWPotential(normalize=1.,a=3.)
    tmax= 3.
    vo,ro= 200., 7.
    o= Orbit([1.,0.5,1.3,0.3,0.1,0.4],ro=ro,vo=vo)
    run_orbitIntegration_comparison(o,np,tmax,vo,ro)
    return None

def test_amuse_HernquistPotential():
    hp= potential.HernquistPotential(normalize=1.,a=3.)
    tmax= 3.
    vo,ro= 210., 7.5
    o= Orbit([1.,0.25,1.4,0.3,-0.1,0.4],ro=ro,vo=vo)
    run_orbitIntegration_comparison(o,hp,tmax,vo,ro,tol=0.02)
    return None

def test_amuse_PowerSphericalPotentialwCutoffPotential():
    pp= potential.PowerSphericalPotentialwCutoff(normalize=1.,alpha=1.,rc=0.4)
    tmax= 2.
    vo,ro= 180., 9.
    o= Orbit([1.,0.03,1.03,0.2,0.1,0.4],ro=ro,vo=vo)
    run_orbitIntegration_comparison(o,pp,tmax,vo,ro)
    return None

def test_amuse_LogarithmicHaloPotential():
    lp= potential.LogarithmicHaloPotential(normalize=1.)
    tmax= 2.
    vo,ro= 210., 8.5
    o= Orbit([1.,0.1,1.1,0.3,0.1,0.4],ro=ro,vo=vo)
    run_orbitIntegration_comparison(o,lp,tmax,vo,ro,tol=0.03)
    return None

def test_amuse_PlummerPotential():
    pp= potential.PlummerPotential(normalize=1.,b=2.)
    tmax= 3.
    vo,ro= 213., 8.23
    o= Orbit([1.,0.1,1.1,0.3,0.1,0.4],ro=ro,vo=vo)
    run_orbitIntegration_comparison(o,pp,tmax,vo,ro,tol=0.03)
    return None

def test_amuse_MWPotential2014():
    mp= potential.MWPotential2014
    tmax= 3.5
    vo,ro= 220., 8.
    o= Orbit([1.,0.1,1.1,0.2,0.1,1.4],ro=ro,vo=vo)
    run_orbitIntegration_comparison(o,mp,tmax,vo,ro)
    return None

def run_orbitIntegration_comparison(orb,pot,tmax,vo,ro,tol=0.01):
    # Integrate in galpy
    ts= numpy.linspace(0.,tmax/bovy_conversion.time_in_Gyr(vo,ro),1001)
    orb.integrate(ts,pot)

    # Integrate with amuse
    x,y,z,vx,vy,vz=integrate_amuse(orb,pot,tmax | units.Gyr, vo,ro)

    # Read and compare

    xdiff= numpy.fabs((x-orb.x(ts[-1]))/x)
    ydiff= numpy.fabs((y-orb.y(ts[-1]))/y)
    zdiff= numpy.fabs((z-orb.z(ts[-1]))/z)
    vxdiff= numpy.fabs((vx-orb.vx(ts[-1]))/vx)
    vydiff= numpy.fabs((vy-orb.vy(ts[-1]))/vy)
    vzdiff= numpy.fabs((vz-orb.vz(ts[-1]))/vz)
    assert xdiff < tol, 'galpy and amuse orbit integration inconsistent for x by %g' % xdiff
    assert ydiff < tol, 'galpy and amuse orbit integration inconsistent for y by %g' % ydiff
    assert zdiff < tol, 'galpy and amuse orbit integration inconsistent for z by %g' % zdiff
    assert vxdiff < tol, 'galpy and amuse orbit integration inconsistent for vx by %g' % vxdiff
    assert vydiff < tol, 'galpy and amuse orbit integration inconsistent for vy by %g' % vydiff
    assert vzdiff < tol, 'galpy and amuse orbit integration inconsistent for vz by %g' % vzdiff

    return None
    
def integrate_amuse(orb,pot,tmax,vo,ro):
    """Integrate a snapshot in infile until tmax in Gyr, save to outfile"""

    time=0.0 | tmax.unit
    dt = tmax/10001.

    orbit = Particles(1)

    orbit.mass= 1. | units.MSun
    orbit.radius = 1. |units.RSun

    orbit.position=[orb.x(),orb.y(),orb.z()] | units.kpc
    orbit.velocity=[orb.vx(),orb.vy(),orb.vz()] | units.kms
    galaxy_code = to_amuse(pot,ro=ro,vo=vo)
    
    orbit_gravity=drift_without_gravity(orbit)
    orbit_gravity.particles.add_particles(orbit)
    channel_from_gravity_to_orbit= orbit_gravity.particles.new_channel_to(orbit)

    gravity = bridge.Bridge(use_threading=False)
    gravity.add_system(orbit_gravity, (galaxy_code,))
    gravity.add_system(galaxy_code,)
    gravity.timestep = dt

    while time <= tmax:
        time += dt
        gravity.evolve_model(time)

    channel_from_gravity_to_orbit.copy()
    gravity.stop()

    return orbit.x[0].value_in(units.kpc),orbit.y[0].value_in(units.kpc),orbit.z[0].value_in(units.kpc),orbit.vx[0].value_in(units.kms),orbit.vy[0].value_in(units.kms),orbit.vz[0].value_in(units.kms)


class drift_without_gravity(object):
    def __init__(self, convert_nbody, time= 0 |units.Myr):
        self.model_time= time
        self.particles=Particles()

    def evolve_model(self, t_end):
        dt= t_end- self.model_time
        self.particles.position += self.particles.velocity*dt
        self.model_time= t_end
    @property
    def potential_energy(self):
        return quantities.zero
    @property
    def get_potential_at_point(self):
        return quantities.zero
    @property
    def kinetic_energy(self):
        return (0.5*self.particles.mass*self.particles.velocity.lengths()**2).sum()
    @property
    def angular_momenum(self):
        return numpy.cross(self.particles.position,self.particles.velocity)
    def stop(self):
        pass

def test_amuse_ChandrasekharDynamicalFrictionForce():
    mp= potential.MWPotential2014
    cdf= potential.ChandrasekharDynamicalFrictionForce(GMs=0.001,rhm=0.,dens=mp)
    tmax= 3.5
    vo,ro= 220., 8.
    o= Orbit([1.,0.1,1.1,0.2,0.1,1.4],ro=ro,vo=vo)
    run_orbitIntegration_comparison_with_friction(o,mp,cdf,tmax,vo,ro)
    return None

def run_orbitIntegration_comparison_with_friction(orb,pot,cdf,tmax,vo,ro,tol=0.03):
    # Integrate in galpy
    ts= numpy.linspace(0.,tmax/bovy_conversion.time_in_Gyr(vo,ro),1001)
    orb.integrate(ts,pot+cdf)

    # Integrate with amuse
    x,y,z,vx,vy,vz=integrate_amuse_with_friction(orb,pot,cdf,tmax | units.Gyr, vo,ro)

    # Read and compare

    xdiff= numpy.fabs((x-orb.x(ts[-1]))/x)
    ydiff= numpy.fabs((y-orb.y(ts[-1]))/y)
    zdiff= numpy.fabs((z-orb.z(ts[-1]))/z)
    vxdiff= numpy.fabs((vx-orb.vx(ts[-1]))/vx)
    vydiff= numpy.fabs((vy-orb.vy(ts[-1]))/vy)
    vzdiff= numpy.fabs((vz-orb.vz(ts[-1]))/vz)
    assert xdiff < tol, 'galpy and amuse orbit integration inconsistent for x by %g' % xdiff
    assert ydiff < tol, 'galpy and amuse orbit integration inconsistent for y by %g' % ydiff
    assert zdiff < tol, 'galpy and amuse orbit integration inconsistent for z by %g' % zdiff
    assert vxdiff < tol, 'galpy and amuse orbit integration inconsistent for vx by %g' % vxdiff
    assert vydiff < tol, 'galpy and amuse orbit integration inconsistent for vy by %g' % vydiff
    assert vzdiff < tol, 'galpy and amuse orbit integration inconsistent for vz by %g' % vzdiff

    return None

def integrate_amuse_with_friction(orb,pot,cdf,tmax,vo,ro):
    """Integrate a snapshot in infile until tmax in Gyr, save to outfile"""

    time=0.0 | tmax.unit
    dt = tmax/10001.

    orbit = Particles(1)

    orbit.mass= 1. | units.MSun
    orbit.radius = 1. |units.RSun

    orbit.position=[orb.x(),orb.y(),orb.z()] | units.kpc
    orbit.velocity=[orb.vx(),orb.vy(),orb.vz()] | units.kms
    galaxy_code = to_amuse(pot,ro=ro,vo=vo)
    cdf_code=amuse_chandrasekhar_dynamical_friction(cdf)
    cdf_code.set_rv(orbit.x[0],orbit.y[0],orbit.z[0],orbit.vx[0],orbit.vy[0],orbit.vz[0])

    orbit_gravity=drift_without_gravity(orbit)
    orbit_gravity.particles.add_particles(orbit)
    channel_from_gravity_to_orbit= orbit_gravity.particles.new_channel_to(orbit)

    gravity = bridge.Bridge(use_threading=False)
    gravity.add_system(orbit_gravity, (galaxy_code,cdf_code,))
    gravity.add_system(galaxy_code,)
    gravity.timestep = dt

    while time <= tmax:
        time += dt
        gravity.evolve_model(time)

        channel_from_gravity_to_orbit.copy()
        cdf_code.set_rv(orbit.x[0],orbit.y[0],orbit.z[0],orbit.vx[0],orbit.vy[0],orbit.vz[0])

    channel_from_gravity_to_orbit.copy()
    gravity.stop()

    return orbit.x[0].value_in(units.kpc),orbit.y[0].value_in(units.kpc),orbit.z[0].value_in(units.kpc),orbit.vx[0].value_in(units.kms),orbit.vy[0].value_in(units.kms),orbit.vz[0].value_in(units.kms)

class amuse_chandrasekhar_dynamical_friction(object):
    def __init__(self, cdf, rmin=0.0008 | units.kpc, time= 0 |units.Myr ):
        self.model_time= time

        self.cdf= potential.to_amuse(cdf)

        self.rmin=rmin

    def set_rv(self,x,y,z,vx,vy,vz):
        self.x=x
        self.y=y
        self.z=z
        
        self.r=numpy.sqrt(self.x**2.+self.y**2.+self.z**2.)
        
        self.vx=vx
        self.vy=vy
        self.vz=vz

    def evolve_model(self, t_end):
        self.cdf.evolve_model(t_end)

    def get_potential_at_point(self,eps,x,y,z):
        return self.cdf.get_potential_at_point(eps,self.x,self.y,self.z)
    
    def get_gravity_at_point(self,eps,x,y,z):

        if self.r < self.rmin:
            self.ax,self.ay,self.az=[0. | units.kms/units.Myr,0. | units.kms/units.Myr,0. | units.kms/units.Myr]
        else:
            self.ax,self.ay,self.az=self.cdf.get_gravity_at_point(eps,self.x,self.y,self.z,self.vx,self.vy,self.vz)

        return self.ax,self.ay,self.az
    
    def mass_density(self,x,y,z):
        return self.cdf.mass_density(eps,self.x,self.y,self.z)
    
    def circular_velocity(self,r):
        return self.cdf.circular_velocity(r)
    
    def enclosed_mass(self,r):
        return self.cdf.enclosed_mass(r)
    
    def stop(self):
        pass
