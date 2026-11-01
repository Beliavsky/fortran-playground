! Independent MIT consumer; see licenses/statistics-services-ten-drivers-MIT.txt.
! Exactly one MPI process; this is an API identity check, not parallel verification.
program main
   use libmpifx_module
   use iso_fortran_env, only: real64
   implicit none
   type(mpifx_comm) :: comm
   real(real64) :: values(7),expected(7),reduced(7)
   integer :: t,i,status,total
   call mpifx_init(error=status)
   call check(status)
   call comm%init(error=status)
   call check(status)
   if(comm%size/=1.or.comm%rank/=0) error stop 'Requires one MPI process'
   do t=1,64
      do i=1,7
         expected(i)=real(t*i-100,real64)/8
      end do
      values=expected
      call mpifx_bcast(comm,values,error=status)
      call check(status)
      if(any(values/=expected)) error stop 'Broadcast identity'
      call mpifx_allreduce(comm,values,reduced,MPI_SUM,error=status)
      call check(status)
      if(any(reduced/=expected)) error stop 'Array reduction identity'
      call mpifx_allreduceip(comm,values,MPI_MAX,error=status)
      call check(status)
      if(any(values/=expected)) error stop 'In-place reduction identity'
      call mpifx_allreduce(comm,t-33,total,MPI_SUM,error=status)
      call check(status)
      if(total/=t-33) error stop 'Scalar reduction identity'
   end do
   call mpifx_finalize(error=status)
   call check(status)
   print '(a)', '64 one-process broadcast/reduction traces; 1,408 exact value references'
   print '(a)', 'PASS mpifx-identity-reference'
contains
   subroutine check(code)
      integer,intent(in) :: code
      if(code/=0) error stop 'MPI wrapper status'
   end subroutine
end program
