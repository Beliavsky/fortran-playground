! Small complex 3-D FFT using the library's built-in CPU backend.
program main
   use mpi
   use decomp_2d, only: decomp_2d_init, decomp_2d_finalize, decomp_log, decomp_info, alloc_x, alloc_z
   use decomp_2d_fft
   use decomp_2d_constants, only: mytype, D2D_LOG_QUIET, &
      DECOMP_2D_FFT_FORWARD, DECOMP_2D_FFT_BACKWARD, PHYSICAL_IN_X
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: nx=8, ny=6, nz=4
   integer :: code, processes, p_row, p_col
   type(decomp_info), pointer :: physical
   complex(mytype), allocatable :: input(:,:,:), output(:,:,:), expected(:,:,:)
   real(mytype) :: forward_error, backward_error
   call MPI_Init(code)
   if (code /= MPI_SUCCESS) error stop 'MPI initialization failed'
   call MPI_Comm_size(MPI_COMM_WORLD, processes, code)
   if (code /= MPI_SUCCESS .or. processes /= 1) error stop 'This example expects one process'
   decomp_log = D2D_LOG_QUIET
   p_row = 1
   p_col = 1
   call decomp_2d_init(nx, ny, nz, p_row, p_col, complex_pool=.true.)
   call decomp_2d_fft_init(PHYSICAL_IN_X)
   physical => decomp_2d_fft_get_ph()
   call alloc_x(input, physical, .true.)
   call alloc_z(output, physical, .true.)
   allocate(expected, mold=input)
   expected = cmplx(0.0_mytype,0.0_mytype,kind=mytype)
   expected(1,1,1) = cmplx(1.0_mytype,0.0_mytype,kind=mytype)
   input = expected
   call decomp_2d_fft_3d(input, output, DECOMP_2D_FFT_FORWARD)
   if (.not. all(ieee_is_finite(real(output))) .or. .not. all(ieee_is_finite(aimag(output)))) &
      error stop 'Nonfinite forward transform'
   forward_error = maxval(abs(output-1.0_mytype))
   if (.not. ieee_is_finite(forward_error) .or. forward_error > 1.0e-12_mytype) &
      error stop 'Impulse transform has incorrect Fourier coefficients'
   call decomp_2d_fft_3d(output, input, DECOMP_2D_FFT_BACKWARD)
   input = input/real(nx*ny*nz,mytype)
   if (.not. all(ieee_is_finite(real(input))) .or. .not. all(ieee_is_finite(aimag(input)))) &
      error stop 'Nonfinite inverse transform'
   backward_error = maxval(abs(input-expected))
   if (.not. ieee_is_finite(backward_error) .or. backward_error > 1.0e-12_mytype) &
      error stop 'Inverse transform did not reconstruct the input'
   deallocate(input, output, expected)
   nullify(physical)
   call decomp_2d_fft_finalize()
   call decomp_2d_finalize()
   call MPI_Finalize(code)
   if (code /= MPI_SUCCESS) error stop 'MPI finalization failed'
   print '(a,es12.4)', 'Forward 3-D FFT maximum error: ', forward_error
   print '(a,es12.4)', 'Inverse 3-D FFT maximum error: ', backward_error
   print '(a)', 'PASS 2decomp-fft'
end program main
