! Single-process CPU/FFTW example based on the author's 2-D complex FFT test.
program main
   use, intrinsic :: iso_fortran_env, only: real64, int32, int64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   use mpi_f08
   use dtfft
   implicit none
   integer(int32), parameter :: nx=8, ny=8
   type(dtfft_plan_c2c_t) :: plan
   complex(real64), pointer :: input(:,:), output(:,:)
   complex(real64) :: expected(nx,ny)
   integer(int32) :: in_counts(2), out_counts(2), code, processes
   integer(int64) :: allocation_size
   real(real64) :: forward_error, backward_error
   call MPI_Init(code)
   call check()
   call MPI_Comm_size(MPI_COMM_WORLD, processes, code)
   call check()
   if (processes /= 1) error stop 'This example expects one MPI process'
   call plan%create([nx,ny], effort=DTFFT_ESTIMATE, executor=DTFFT_EXECUTOR_FFTW3, error_code=code)
   call check()
   call plan%get_local_sizes(in_counts=in_counts, out_counts=out_counts, &
      alloc_size=allocation_size, error_code=code)
   call check()
   if (any(in_counts /= [nx,ny])) error stop 'Unexpected local input shape'
   call plan%mem_alloc(allocation_size, input, in_counts, error_code=code)
   call check()
   call plan%mem_alloc(allocation_size, output, out_counts, error_code=code)
   call check()
   expected = cmplx(0.0_real64,0.0_real64,kind=real64)
   expected(1,1) = cmplx(1.0_real64,0.0_real64,kind=real64)
   input = expected
   call plan%execute(input, output, DTFFT_EXECUTE_FORWARD, error_code=code)
   call check()
   forward_error = maxval(abs(output-1.0_real64))
   if (.not. ieee_is_finite(forward_error) .or. forward_error > 1.0e-12_real64) &
      error stop 'Impulse transform should have all coefficients equal to one'
   output = output/real(nx*ny,real64)
   call plan%execute(output, input, DTFFT_EXECUTE_BACKWARD, error_code=code)
   call check()
   backward_error = maxval(abs(input-expected))
   if (.not. ieee_is_finite(backward_error) .or. backward_error > 1.0e-12_real64) &
      error stop 'Inverse transform did not recover the impulse'
   call plan%mem_free(input, code)
   call check()
   call plan%mem_free(output, code)
   call check()
   call plan%destroy(error_code=code)
   call check()
   call MPI_Finalize(code)
   call check()
   print '(a,es12.4)', 'Forward FFT maximum error: ', forward_error
   print '(a,es12.4)', 'Inverse FFT maximum error: ', backward_error
   print '(a)', 'PASS dtfft'
contains
   subroutine check()
      if (code /= 0) then
         print '(a,i0)', 'MPI/dtFFT error: ', code
         error stop 'Operation failed'
      end if
   end subroutine check
end program main
