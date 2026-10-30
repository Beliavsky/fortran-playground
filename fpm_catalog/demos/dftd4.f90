! DFT-D4 PBE two-body reference: test_pbed4_mb01 in the pinned upstream tests.
! MB16-43/01 geometry adapted from mstore v0.4.0 (Apache-2.0).
! SPDX-License-Identifier: LGPL-3.0-or-later AND Apache-2.0
program main
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   use dftd4, only: d4_model, new_d4_model, rational_damping_param, &
      get_dispersion, realspace_cutoff
   use mctc_env, only: wp, error_type
   use mctc_io, only: new, structure_type
   implicit none
   integer, parameter :: nat = 16
   character(len=*), parameter :: sym(nat) = [character(len=4)::&
      & "Na", "H", "O", "H", "F", "H", "H", "O", "N", "H", "H", "Cl", "B", "B", "N", "Al"]
   real(wp), parameter :: xyz(3, nat) = reshape([&
      & -1.85528263484662_wp,  3.58670515364616_wp, -2.41763729306344_wp, &
      &  4.40178023537845_wp,  0.02338844412653_wp, -4.95457749372945_wp, &
      & -2.98706033463438_wp,  4.76252065456814_wp,  1.27043301573532_wp, &
      &  0.79980886075526_wp,  1.41103455609189_wp, -5.04655321620119_wp, &
      & -4.20647469409936_wp,  1.84275767548460_wp,  4.55038084858449_wp, &
      & -3.54356121843970_wp, -3.18835665176557_wp,  1.46240021785588_wp, &
      &  2.70032160109941_wp,  1.06818452504054_wp, -1.73234650374438_wp, &
      &  3.73114088824361_wp, -2.07001543363453_wp,  2.23160937604731_wp, &
      & -1.75306819230397_wp,  0.35951417150421_wp,  1.05323406177129_wp, &
      &  5.41755788583825_wp, -1.57881830078929_wp,  1.75394002750038_wp, &
      & -2.23462868255966_wp, -2.13856505054269_wp,  4.10922285746451_wp, &
      &  1.01565866207568_wp, -3.21952154552768_wp, -3.36050963020778_wp, &
      &  2.42119255723593_wp,  0.26626435093114_wp, -3.91862474360560_wp, &
      & -3.02526098819107_wp,  2.53667889095925_wp,  2.31664984740423_wp, &
      & -2.00438948664892_wp, -2.29235136977220_wp,  2.19782807357059_wp, &
      &  1.12226554109716_wp, -1.36942007032045_wp,  0.48455055461782_wp],&
      & shape(xyz))

   real(wp), parameter :: reference = -1.8578752883363366e-2_wp
   real(wp), parameter :: step = 1.0e-5_wp
   real(wp) :: energy, plus, minus, translated, fd_error
   real(wp) :: gradient(3,nat), scratch(3,nat), positions(3,nat)

   call evaluate(xyz, energy, gradient)
   if (abs(energy-reference) > 1.0e-10_wp) error stop 'upstream energy reference'
   if (maxval(abs(sum(gradient,dim=2))) > 1.0e-9_wp) error stop 'net force'
   positions=xyz
   positions(1,1)=positions(1,1)+step
   call evaluate(positions,plus,scratch)
   positions(1,1)=positions(1,1)-2*step
   call evaluate(positions,minus,scratch)
   fd_error=abs((plus-minus)/(2*step)-gradient(1,1))
   if (fd_error > 1.0e-6_wp) error stop 'finite-difference gradient'
   positions=xyz+1.25_wp
   call evaluate(positions,translated,scratch)
   if (abs(translated-energy) > 1.0e-11_wp) error stop 'translation invariance'
   print '(a,f20.14)', 'PBE-D4 dispersion energy (Hartree): ',energy
   print '(a,es12.4)', 'Absolute reference error: ',abs(energy-reference)
   print '(a,es12.4)', 'Gradient finite-difference error: ',fd_error
   print '(a)', 'PASS dftd4'
contains
   subroutine evaluate(pos,e,g)
      real(wp), intent(in) :: pos(3,nat)
      real(wp), intent(out) :: e,g(3,nat)
      type(structure_type) :: mol
      type(d4_model) :: model
      type(error_type), allocatable :: error
      type(rational_damping_param), parameter :: param=rational_damping_param( &
         s6=1.0_wp,s9=0.0_wp,alp=16.0_wp, &
         s8=0.95948085_wp,a1=0.38574991_wp,a2=4.80688534_wp)
      real(wp) :: sigma(3,3)
      call new(mol,sym,pos)
      call new_d4_model(error,model,mol)
      if (allocated(error)) then
         print '(a)',error%message
         error stop 'D4 model initialization'
      end if
      call get_dispersion(mol,model,param,realspace_cutoff(),e,g,sigma)
      if (.not.ieee_is_finite(e)) error stop 'nonfinite energy'
      if (.not.all(ieee_is_finite(g))) error stop 'nonfinite gradient'
   end subroutine evaluate
end program main
