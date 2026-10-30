! Periodic silicon distances, adapted from RAFFLE's test/test_dist_calcs.f90.
! RAFFLE v1.0.0 is GPL-3.0; original library sources are unchanged.
program main
   use raffle__constants, only: real32
   use raffle__geom_rw, only: basis_type
   use raffle__misc_linalg, only: modu
   use raffle__dist_calcs, only: get_min_dist, get_min_dist_between_point_and_atom
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(basis_type) :: cell
   real(real32) :: point(3), distance, expected, nearest
   integer :: i
   cell%sysname='Silicon'
   cell%nspec=1
   cell%natom=2
   allocate(cell%spec(1))
   cell%spec(1)%num=2
   cell%spec(1)%name='Si'
   allocate(cell%spec(1)%atom(2,3))
   cell%spec(1)%atom(1,:)=[0.0_real32,0.0_real32,0.0_real32]
   cell%spec(1)%atom(2,:)=[0.25_real32,0.25_real32,0.25_real32]
   cell%lat(1,:)=[0.0_real32,2.14_real32,2.14_real32]
   cell%lat(2,:)=[2.14_real32,0.0_real32,2.14_real32]
   cell%lat(3,:)=[2.14_real32,2.14_real32,0.0_real32]
   ! Each point is close to the origin or an equivalent periodic image.
   do i=1,3
      point=real(i,real32)-0.1_real32
      expected=sqrt(3.0_real32)*0.428_real32
      distance=get_min_dist_between_point_and_atom(cell,loc=point,atom=[1,1])
      nearest=modu(get_min_dist(cell,loc=point,lignore_close=.true.))
      if (.not.ieee_is_finite(distance) .or. .not.ieee_is_finite(nearest)) error stop 'Nonfinite distance'
      if (abs(distance-expected)>3.0e-6_real32) error stop 'Atom-distance check'
      if (abs(nearest-expected)>3.0e-6_real32) error stop 'Nearest-atom check'
      print '(a,f5.2,a,f12.7)', 'Fractional point (t,t,t), t=',point(1),'; nearest distance: ',nearest
   end do
   print '(a)', 'PASS raffle'
end program main
