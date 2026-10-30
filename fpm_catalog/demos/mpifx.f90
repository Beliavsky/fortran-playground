! Single-process illustration of the typed MPI wrappers; no speedup is implied.
program main
   use libmpifx_module
   use, intrinsic :: iso_fortran_env, only: real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(mpifx_comm) :: comm
   real(real64) :: values(3), reduced(3), expected(3)
   integer :: total, status
   call mpifx_init(error=status)
   if (status /= 0) error stop 'MPI initialization failed'
   call comm%init(error=status)
   if (status /= 0) error stop 'Communicator initialization failed'
   if (comm%size /= 1) error stop 'This example uses exactly one MPI process'
   expected = [1.25_real64, -2.5_real64, 4.0_real64]
   values = expected
   call mpifx_bcast(comm, values, error=status)
   if (status /= 0 .or. any(values /= expected)) error stop 'Broadcast failed'
   call mpifx_allreduce(comm, values, reduced, MPI_SUM, error=status)
   if (status /= 0) error stop 'Array reduction failed'
   if (.not. all(ieee_is_finite(reduced))) error stop 'Nonfinite reduction'
   if (maxval(abs(reduced-expected)) > 1.0e-12_real64) error stop 'Array sum mismatch'
   call mpifx_allreduce(comm, 7, total, MPI_SUM, error=status)
   if (status /= 0 .or. total /= 7) error stop 'Integer reduction failed'
   call mpifx_allreduceip(comm, values, MPI_MAX, error=status)
   if (status /= 0 .or. any(values /= expected)) error stop 'In-place maximum failed'
   print '(a,i0)', 'MPI processes: ', comm%size
   print '(a,3f10.4)', 'Broadcast and reduced vector: ', reduced
   print '(a,i0)', 'Reduced integer: ', total
   call mpifx_finalize(error=status)
   if (status /= 0) error stop 'MPI finalization failed'
   print '(a)', 'PASS mpifx'
end program main
