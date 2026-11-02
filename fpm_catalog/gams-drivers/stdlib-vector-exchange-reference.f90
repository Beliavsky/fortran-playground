! Independent MIT consumer; see licenses/grids-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_math, only: swap
   implicit none

   real(real64),allocatable :: a(:),b(:),a0(:),b0(:)
   complex(real64),allocatable :: z(:),w(:),z0(:),w0(:)
   integer(int64),allocatable :: ia(:),ib(:),ia0(:),ib0(:)
   real(real64) :: slices(20),before(20)
   integer :: n,i
   do n=0,64
      a=[(real(i,real64)/8,i=1,n)]; b=[(real(-i-2,real64)/4,i=1,n)]; a0=a; b0=b
      z=cmplx(a,b,real64); w=cmplx(b,-a,real64); z0=z; w0=w
      ia=[(int(i,int64)*100000000000_int64,i=1,n)]; ib=-ia-7; ia0=ia; ib0=ib
      call swap(a,b); call swap(z,w); call swap(ia,ib)
      if(any(a/=b0).or.any(b/=a0)) error stop 'Real exchange reference'
      if(any(z/=w0).or.any(w/=z0)) error stop 'Complex exchange reference'
      if(any(ia/=ib0).or.any(ib/=ia0)) error stop 'Integer exchange reference'
      call swap(a,b); call swap(z,w); call swap(ia,ib)
      if(any(a/=a0).or.any(b/=b0)) error stop 'Real inverse exchange'
      if(any(z/=z0).or.any(w/=w0)) error stop 'Complex inverse exchange'
      if(any(ia/=ia0).or.any(ib/=ib0)) error stop 'Integer inverse exchange'
   end do
   slices=[(real(i,real64),i=1,20)]; before=slices
   call swap(slices(1:9:2),slices(12:20:2))
   do i=1,5
      if(slices(2*i-1)/=before(2*i+10).or.slices(2*i+10)/=before(2*i-1)) error stop 'Strided exchange'
   end do
   if(any(slices(2:10:2)/=before(2:10:2)).or.any(slices(11:19:2)/=before(11:19:2))) &
      error stop 'Untouched slice elements'
   print '(a)', 'Vector exchange: lengths 0..64, three kinds, inverse exchange and disjoint strided slices'
   print '(a)', 'PASS stdlib-vector-exchange-reference'
end program
