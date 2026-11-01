! Independent MIT consumer; see licenses/workflows-ten-drivers-MIT.txt.
program main
   implicit none
   integer :: trial
   do trial=1,8
      call fixture(trial)
   end do
   print '(a)', 'Eight integer/string list traces: append, middle insert/delete, lookup and absent search'
   print '(a)', 'PASS fy-list-reference'
contains
   subroutine fixture(t)
      use type_intlist, only: IntList,IntList_init,int_size=>size
      use type_stringlist, only: StringList,StringList_init,string_size=>size
      integer,intent(in) :: t
      type(IntList),allocatable :: numbers
      type(StringList),allocatable :: words
      integer :: oracle(128),n,step,j,k,value
      character(24) :: text,expected
      allocate(numbers,words)
      call IntList_init(numbers)
      call StringList_init(words)
      n=0
      do step=1,48
         n=n+1
         oracle(n)=1000*t+step
         call numbers%append(oracle(n))
         write(text,'(a,i0)') 'word-',step
         call words%append(trim(text))
         if(string_size(words)/=step) error stop 'String list size'
         if(mod(step,3)==0) then
            k=max(1,n/2)
            oracle(k+1:n+1)=oracle(k:n)
            value=-1000*t-step
            oracle(k)=value
            n=n+1
            call numbers%insert(k,value)
         end if
         if(mod(step,4)==0) then
            k=max(1,n/3)
            call numbers%delete(k)
            oracle(k:n-1)=oracle(k+1:n)
            n=n-1
         end if
         if(int_size(numbers)/=n) error stop 'Integer list size'
         do j=n,1,-1
            if(numbers%get(j)/=oracle(j)) error stop 'Integer sequence oracle'
            if(numbers%find(oracle(j))/=j) error stop 'Integer lookup'
         end do
         if(numbers%find(999999)/=0) error stop 'Absent integer'
         do j=step,1,-1
            write(expected,'(a,i0)') 'word-',j
            if(words%get(j)/=trim(expected)) error stop 'String sequence oracle'
            if(words%find(trim(expected))/=j) error stop 'String lookup'
         end do
         if(words%find('absent')/=0) error stop 'Absent string'
      end do
      deallocate(numbers,words)
   end subroutine
end program
