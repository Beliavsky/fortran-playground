! Independent API consumer; MIT: licenses/graph-neighbors-drivers-MIT.txt.
program main
   use iso_fortran_env,only:int32,int64,real32,real64
   use m_sort,only:sort
   implicit none
   integer,parameter::lengths(*)=[0,1,2,3,4,7,8,15,16,31,32,63,64,127]
   integer(int32),allocatable::a(:)
   integer::n,i,j,pattern,fixtures,calls,permutations
   fixtures=0; calls=0; permutations=0
   do n=1,7
      a=[(int(i,int32),i=1,n)]
      call permute(1)
   end do
   do j=1,size(lengths)
      n=lengths(j)
      if (allocated(a)) deallocate(a)
      allocate(a(n))
      do pattern=1,6
         do i=1,n
            select case(pattern)
            case(1)
               a(i)=i-n/2
            case(2)
               a(i)=n-i
            case(3)
               a(i)=7
            case(4)
               a(i)=mod(i,3)-1
            case(5)
               a(i)=(-1)**i*i
            case(6)
               a(i)=mod(37*i+11,17)-8
            end select
         end do
         call check_rank()
      end do
   end do
   if (permutations/=5913.or.fixtures/=5997.or.calls/=71964) error stop 'accounting'
   print '(a,i0)', 'Exhaustive permutations through length seven: ',permutations
   print '(a,i0,a,i0)', 'Total sorting fixtures: ',fixtures,'; typed sorting calls: ',calls
   print '(a)', 'Integer32/64 and real32/64; default, stable=false and stable=true settings.'
   print '(a)', 'Independent insertion-sort values; empty input, repeated keys and boundary sizes.'
   print '(a)', 'PASS coretran-sort-reference'
contains
   recursive subroutine permute(first)
      integer,intent(in)::first
      integer::k,temp
      if (first>size(a)) then
         call check_rank()
         permutations=permutations+1
         return
      end if
      do k=first,size(a)
         temp=a(first); a(first)=a(k); a(k)=temp
         call permute(first+1)
         temp=a(first); a(first)=a(k); a(k)=temp
      end do
   end subroutine
   subroutine check_rank()
      integer::expected(size(a)),iv(size(a)),i,j,temp,setting
      integer(int64)::large(size(a))
      real(real32)::single(size(a))
      real(real64)::double(size(a))
      expected=a
      do i=2,size(a)
         temp=expected(i); j=i-1
         do while(j>=1)
            if (expected(j)<=temp) exit
            expected(j+1)=expected(j); j=j-1
         end do
         expected(j+1)=temp
      end do
      do setting=1,3
         if (size(a)==16) print *, 'Size-16 data and setting:',a,setting
         iv=a; large=int(a,int64)*10000000000_int64+3_int64
         single=real(a,real32)/8; double=real(a,real64)/8
         select case(setting)
         case(1)
            call sort(iv); call sort(large); call sort(single); call sort(double)
         case(2)
            call sort(iv,stable=.false.); call sort(large,stable=.false.)
            call sort(single,stable=.false.); call sort(double,stable=.false.)
         case(3)
            call sort(iv,stable=.true.); call sort(large,stable=.true.)
            call sort(single,stable=.true.); call sort(double,stable=.true.)
         end select
         if (any(iv/=expected)) error stop 'integer32 sorted reference'
         if (any(large/=int(expected,int64)*10000000000_int64+3_int64)) error stop 'integer64 sorted reference'
         if (any(single/=real(expected,real32)/8)) error stop 'real32 sorted reference'
         if (any(double/=real(expected,real64)/8)) error stop 'real64 sorted reference'
         calls=calls+4
      end do
      fixtures=fixtures+1
   end subroutine
end program
