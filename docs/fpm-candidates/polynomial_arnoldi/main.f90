program demo_polynomial_arnoldi
   use stdlib_linalg_constants, only: dp,ilp
   use specialmatrices, only: Poisson2D,matmul
   use polynomial_arnoldi, only: gmres,pp_gmres
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer(ilp), parameter :: nx=8,ny=7,n=nx*ny
   type(Poisson2D) :: operator
   real(dp) :: exact(n),b(n),error,residual
   real(dp), allocatable :: ordinary(:),preconditioned(:)
   integer :: i
   operator = Poisson2D(nx,ny)
   exact = [(sin(0.17_dp*i)+cos(0.31_dp*i),i=1,n)]
   b = matmul(operator,exact)
   ordinary = gmres(operator,b,kmax=20,maxiter=500)
   preconditioned = pp_gmres(operator,b,kmax=20,deg=6,maxiter=500)
   if (.not. all(ieee_is_finite(ordinary))) error stop 'Nonfinite GMRES solution'
   if (.not. all(ieee_is_finite(preconditioned))) error stop 'Nonfinite preconditioned solution'
   error = maxval(abs(ordinary-exact))
   residual = norm2(matmul(operator,ordinary)-b)/norm2(b)
   print '(a,2es14.5)', 'GMRES:       max solution error, relative residual: ',error,residual
   if (error>1e-5_dp .or. residual>1e-6_dp) error stop 'GMRES check failed'
   error = maxval(abs(preconditioned-exact))
   residual = norm2(matmul(operator,preconditioned)-b)/norm2(b)
   print '(a,2es14.5)', 'PP-GMRES:    max solution error, relative residual: ',error,residual
   if (error>1e-5_dp .or. residual>1e-6_dp) error stop 'Preconditioned GMRES check failed'
   print '(a)', 'PASS polynomial_arnoldi'
end program
