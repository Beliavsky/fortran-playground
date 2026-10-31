! Independent API consumer; see licenses/periodic-calculus-drivers-MIT.txt.
program checked_raffle_distances
   use raffle__constants, only: real32
   use iso_fortran_env, only: real64
   use raffle__geom_rw, only: basis_type
   use raffle__dist_calcs, only: get_min_dist,get_min_dist_between_point_and_atom
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(real32), parameter :: atoms(3,5)=reshape([0.,0.,0., 0.25,0.125,0.375, &
      0.75,0.5,0.125, 0.125,0.625,0.875, 0.5,0.75,0.25],[3,5])
   integer, parameter :: shifts(3,3)=reshape([0,0,0,2,-3,1,-2,1,3],[3,3])
   integer :: shape,rotation,queries=0,references=0
   real(real64) :: worst=0
   do shape=1,3
      do rotation=0,1
         call fixture(shape,rotation)
      end do
   end do
   print '(a,i0)', 'Orthogonal cell queries: ',queries
   print '(a,i0)', 'Periodic distance references: ',references
   print '(a,es12.4)', 'Maximum cell-scaled distance error: ',worst
   print '(a)', 'PASS raffle-orthogonal-reference'
contains
   subroutine fixture(shape,rotation)
      integer, intent(in) :: shape,rotation
      type(basis_type) :: cell
      real(real32) :: point(3),base(3),lat(3,3),u(3),v(3),real_vector(3),fractional_vector(3),got
      real(real64) :: expected(5),nearest,cart(3),scale,error,angle,c,s
      integer :: i,j,query,translation,species,atom,k
      cell%nspec=2; cell%natom=5
      allocate(cell%spec(2))
      cell%spec(1)%num=3; cell%spec(2)%num=2
      cell%spec(1)%name='Si'; cell%spec(2)%name='O'
      allocate(cell%spec(1)%atom(3,3),cell%spec(2)%atom(2,3))
      do i=1,3
         cell%spec(1)%atom(i,:)=atoms(:,i)
      end do
      do i=1,2
         cell%spec(2)%atom(i,:)=atoms(:,i+3)
      end do
      lat=0
      select case(shape)
      case(1)
         lat(1,1)=1; lat(2,2)=1; lat(3,3)=1
      case(2)
         lat(1,1)=1; lat(2,2)=2; lat(3,3)=3
      case(3)
         lat(1,1)=0.5; lat(2,2)=1.5; lat(3,3)=2
      end select
      if (rotation==1) then
         angle=0.37_real64; c=cos(angle); s=sin(angle)
         u=lat(:,1); v=lat(:,2)
         lat(:,1)=real(c*real(u,real64)-s*real(v,real64),real32)
         lat(:,2)=real(s*real(u,real64)+c*real(v,real64),real32)
         angle=0.21_real64; c=cos(angle); s=sin(angle)
         u=lat(:,2); v=lat(:,3)
         lat(:,2)=real(c*real(u,real64)-s*real(v,real64),real32)
         lat(:,3)=real(s*real(u,real64)+c*real(v,real64),real32)
      end if
      cell%lat=lat
      scale=maxval(sqrt(sum(real(lat,real64)**2,dim=2)))
      do query=1,20
         if (query<=15) then
            base=[real(mod(7*query,17),real32)/17,real(mod(11*query,19),real32)/19, &
               real(mod(13*query,23),real32)/23]
         else
            base=atoms(:,query-15)
         end if
         do translation=1,3
            point=base+real(shifts(:,translation),real32)
            do i=1,5
               expected(i)=image_reference(point,atoms(:,i),lat)
               species=1; atom=i
               if (i>3) then
                  species=2; atom=i-3
               end if
               got=get_min_dist_between_point_and_atom(cell,point,[species,atom])
               if (.not.ieee_is_finite(got)) error stop 'nonfinite atom distance'
               call compare(real(got,real64),expected(i),scale)
            end do
            nearest=minval(expected)
            real_vector=get_min_dist(cell,point,lignore_close=.false.,lreal=.true.)
            fractional_vector=get_min_dist(cell,point,lignore_close=.false.,lreal=.false.)
            if (.not.all(ieee_is_finite(real_vector)).or..not.all(ieee_is_finite(fractional_vector))) &
               error stop 'nonfinite nearest vector'
            call compare(norm2(real(real_vector,real64)),nearest,scale)
            cart=0
            do j=1,3
               do k=1,3
                  cart(k)=cart(k)+real(fractional_vector(j),real64)*real(lat(j,k),real64)
               end do
            end do
            call compare(norm2(cart),nearest,scale)
            queries=queries+1
         end do
      end do
   end subroutine fixture
   function image_reference(point,atom,lat) result(distance)
      real(real32), intent(in) :: point(3),atom(3),lat(3,3)
      real(real64) :: distance,wrapped(3),delta(3),cart(3)
      integer :: a,b,c,j,k
      ! Enumerate images of the rounded inputs; do not use componentwise nearest-integer wrapping.
      wrapped=real(point,real64)-floor(real(point,real64))
      distance=huge(1.0_real64)
      do a=-4,4
         do b=-4,4
            do c=-4,4
               delta=wrapped-real(atom,real64)+real([a,b,c],real64)
               cart=0
               do j=1,3
                  do k=1,3
                     cart(k)=cart(k)+delta(j)*real(lat(j,k),real64)
                  end do
               end do
               distance=min(distance,norm2(cart))
            end do
         end do
      end do
   end function image_reference
   subroutine compare(got,expected,scale)
      real(real64), intent(in) :: got,expected,scale
      real(real64) :: error
      error=abs(got-expected)/scale
      worst=max(worst,error)
      if (error>128*real(epsilon(1.0_real32),real64)) error stop 'periodic image minimum mismatch'
      references=references+1
   end subroutine compare
end program checked_raffle_distances
