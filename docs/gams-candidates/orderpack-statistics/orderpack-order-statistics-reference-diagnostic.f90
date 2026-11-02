! Independent MIT consumer; see licenses/ordering-runge-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use M_orderpack,only:orderloc,orderval,orderval_special
   implicit none
   real(wp),allocatable::x(:),sorted(:),work(:),ref(:)
   integer,allocatable::indices(:),counts(:)
   real(wp)::t,expected
   integer::n,i,j,k,pattern,nu,nref,loc,cases
   cases=0
   do n=1,65
      allocate(x(n),sorted(n),work(n),ref(n),indices(n),counts(n))
      do pattern=1,5
         do i=1,n
            select case(pattern)
            case(1)
               x(i)=real(modulo(17*i+3*n,23)-11,wp)/4
            case(2)
               x(i)=real(i/3,wp)/4
            case(3)
               x(i)=-real(i/3,wp)/4
            case(4)
               x(i)=-0.75_wp
            case(5)
               x(i)=real(modulo(37*(i-1),67)-33,wp)/4
            end select
         end do
         sorted=x
         call insertion_sort(sorted)
         do k=1,n
            loc=orderloc(x,k)
            if(loc<1.or.loc>n) error stop 'Order index bounds'
            if(x(loc)/=sorted(k)) then
               print *, 'n, pattern, k, index, actual, expected:',n,pattern,k,loc,x(loc),sorted(k)
               error stop 'Order location value'
            end if
            if(orderval(x,k)/=sorted(k)) error stop 'Order value'
            if(orderval_special(x,k)/=sorted(k)) error stop 'Special order value'
         end do
         cases=cases+1
      end do
      deallocate(x,sorted,work,ref,indices,counts)
   end do
   print '(a,i0)', 'Checked finite REAL64 data sets: ',cases
   print '(a)', 'All order statistics checked through index and two value APIs; equal values may use any matching index.'
   print '(a)', 'PASS orderpack-order-statistics-reference'
contains
   subroutine insertion_sort(a)
      real(wp),intent(inout)::a(:)
      real(wp)::v
      integer::p,q
      do p=2,size(a)
         v=a(p);q=p-1
         do while(q>=1)
            if(a(q)<=v) exit
            a(q+1)=a(q);q=q-1
         end do
         a(q+1)=v
      end do
   end subroutine
end program
