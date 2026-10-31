! Independent API probe; see fpm_catalog/gams-drivers/licenses/periodic-calculus-drivers-MIT.txt.
program skew_image_reference
   use raffle__constants, only: real32
   use iso_fortran_env, only: real64
   use raffle__geom_rw, only: basis_type
   use raffle__dist_calcs, only: get_min_dist_between_point_and_atom
   implicit none
   type(basis_type) :: cell
   real(real32) :: point(3),got
   real(real64) :: delta(3),cart(3),expected
   integer :: a,b,c
   cell%nspec=1; cell%natom=1
   allocate(cell%spec(1)); cell%spec(1)%num=1; cell%spec(1)%name='Si'
   allocate(cell%spec(1)%atom(1,3)); cell%spec(1)%atom=0
   cell%lat(1,:)=[1.0_real32,0.0_real32,0.0_real32]
   cell%lat(2,:)=[0.8_real32,0.6_real32,0.0_real32]
   cell%lat(3,:)=[0.0_real32,0.0_real32,1.0_real32]
   point=[0.49_real32,0.49_real32,0.0_real32]
   expected=huge(1.0_real64)
   do a=-2,2
      do b=-2,2
         do c=-2,2
            delta=real(point,real64)+real([a,b,c],real64)
            cart=matmul(delta,real(cell%lat,real64))
            expected=min(expected,norm2(cart))
         end do
      end do
   end do
   got=get_min_dist_between_point_and_atom(cell,point,[1,1])
   print '(a,es24.16)', 'Returned distance: ',got
   print '(a,es24.16)', 'Independent periodic minimum: ',expected
   if (abs(real(got,real64)-expected)>1e-5_real64) error stop 'skew-cell nearest-image mismatch'
   print '(a)', 'PASS raffle-skew-probe'
end program skew_image_reference
