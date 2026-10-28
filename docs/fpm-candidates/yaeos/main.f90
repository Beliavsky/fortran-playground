! Pure methane: Peng-Robinson pressure, bar; V in litres/mol, T in kelvin.
program demo_yaeos
   use yaeos, only: pr, ArModel, PengRobinson76
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   class(ArModel), allocatable :: model
   real(pr), parameter :: tc=190.564_pr, pc=45.99_pr, omega=0.01142_pr
   real(pr), parameter :: gas_r=0.08314462618_pr, temperature=300.0_pr, volume=1.0_pr
   real(pr) :: pressure, reference, a, b, kappa, alpha

   model = PengRobinson76([tc],[pc],[omega])
   call model%pressure([1.0_pr],V=volume,T=temperature,P=pressure)
   kappa = 0.37464_pr + 1.54226_pr*omega - 0.26992_pr*omega**2
   alpha = (1.0_pr+kappa*(1.0_pr-sqrt(temperature/tc)))**2
   a = 0.45724_pr*gas_r**2*tc**2/pc
   b = 0.07780_pr*gas_r*tc/pc
   reference = gas_r*temperature/(volume-b) - a*alpha/(volume**2+2*b*volume-b*b)
   if (.not. ieee_is_finite(pressure)) error stop 'Nonfinite pressure'
   ! Rounded published PR coefficients differ slightly from exact cubic constants.
   if (abs(pressure-reference) > 0.002_pr) error stop 'Pressure differs from independent PR formula'
   print '(a,f12.6)', 'Methane pressure (bar): ',pressure
   print '(a,f12.6)', 'Independent PR formula: ',reference
   print '(a,f12.6)', 'Ideal-gas pressure:     ',gas_r*temperature/volume
   print '(a)', 'PASS yaeos'
end program
