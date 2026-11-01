! Independent MIT API consumer; see licenses/data-ten-drivers-MIT.txt.
program set_reference
   use, intrinsic :: iso_c_binding, only: c_int32_t,c_int64_t
   use integer32_set, only: int32_set,new_int32_set
   use integer64_set, only: int64_set,new_int64_set
   implicit none
   type(int32_set) :: small
   type(int64_set) :: large
   logical :: present(-50:50),seen(-50:50)
   integer(c_int64_t), parameter :: offset=5000000000_c_int64_t
   integer :: scenario,i,j,value,n,previous,checks,entries
   checks=0; entries=0
   do scenario=1,8
      small=new_int32_set(); large=new_int64_set(); present=.false.
      do i=1,240
         value=modulo(i*(scenario+1)+i/7,101)-50
         if (modulo(i,5)==0) then
            call small%pop(int(value,c_int32_t)); call large%pop(offset+value); present(value)=.false.
         else
            call small%push(int(value,c_int32_t)); call large%push(offset+value); present(value)=.true.
         end if
         call check()
      end do
      call small%sort(); previous=-51
      do j=1,small%size
         if (small%data(j)<=previous) error stop 'integer32 sorted uniqueness'
         previous=small%data(j)
      end do
      call check()
      call small%clear(); call large%clear(); present=.false.; call check()
      call small%push(-50_c_int32_t); call large%push(offset-50); present(-50)=.true.; call check()
      call small%destroy(); call large%destroy()
   end do
   print '(a,i0,a,i0)', 'Eight paired 32/64-bit set traces; membership checks: ',checks,'; values checked: ',entries
   print '(a)', 'Boolean-domain oracle; duplicate insertion, absent/present removal, clear/reuse and 32-bit sorting.'
   print '(a)', '64-bit values exceed 32-bit range; 64-bit sorting, extreme integer bounds and destroy reuse unverified.'
   print '(a)', 'PASS integer-set-reference'
contains
   subroutine check()
      integer :: k
      n=count(present)
      if (small%size/=n .or. large%size/=n) error stop 'set size reference'
      seen=.false.
      do j=1,n
         k=small%data(j)
         if (k< -50 .or. k>50) error stop '32-bit set domain'
         if (seen(k)) error stop '32-bit set duplicate'
         seen(k)=.true.
      end do
      if (any(seen .neqv. present)) error stop '32-bit membership reference'
      seen=.false.
      do j=1,n
         if (large%data(j)<offset-50 .or. large%data(j)>offset+50) error stop '64-bit set domain'
         k=int(large%data(j)-offset)
         if (seen(k)) error stop '64-bit set duplicate'
         seen(k)=.true.
      end do
      if (any(seen .neqv. present)) error stop '64-bit membership reference'
      checks=checks+1; entries=entries+2*n
   end subroutine
end program
