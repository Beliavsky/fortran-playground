! Independent API consumer; see licenses/lu-orbits-drivers-MIT.txt.
program checked_linalg_lu
   use iso_fortran_env, only: real64,int32
   use ieee_arithmetic, only: ieee_is_finite,ieee_is_nan
   use linalg, only: lu_factor,solve_lu
   implicit none
   integer, parameter :: sizes(6)=[1,2,3,5,8,13],singular_sizes(4)=[1,2,5,8]
   integer :: s,pattern,scale,order,fixtures=0,solves=0,entries=0,rejections=0,pivoted=0
   real(real64) :: worst_solution=0,worst_residual=0,worst_factor=0
   do s=1,size(sizes)
      do pattern=1,4
         do scale=1,2
            do order=1,2
               call fixture(sizes(s),pattern,scale,order)
            end do
         end do
      end do
   end do
   do s=1,size(singular_sizes)
      call singular(singular_sizes(s),1)
      call singular(singular_sizes(s),2)
   end do
   if (pivoted==0) error stop 'pivoting not exercised'
   print '(a,i0)', 'Nonsingular factorizations: ',fixtures
   print '(a,i0)', 'Vector/matrix solve calls: ',solves
   print '(a,i0)', 'Known solution entries: ',entries
   print '(a,i0)', 'Singular NaN diagnostics: ',rejections
   print '(a,i0)', 'Factorizations with row swaps: ',pivoted
   print '(a,es12.4)', 'Maximum normalized solution error: ',worst_solution
   print '(a,es12.4)', 'Maximum scaled residual: ',worst_residual
   print '(a,es12.4)', 'Maximum scaled factorization error: ',worst_factor
   print '(a)', 'PASS linalg-lu-reference'
contains
   subroutine fixture(n,pattern,scale,order)
      integer, intent(in) :: n,pattern,scale,order
      real(real64) :: base(n,n),a(n,n),saved(n,n),truth(n,3),b(n,3),bsave(n,3),factor_error,value
      real(real64), allocatable :: packed(:,:),l(:,:),u(:,:),p(:,:),x(:),many(:,:),packed_copy(:,:)
      integer(int32), allocatable :: ipvt(:)
      integer :: i,j,k,r,rows(n),tmp
      base=0
      do i=1,n
         do j=1,n
            select case(pattern)
            case(1)
               if (i/=j) base(i,j)=real(mod(7*i+3*j,11)-5,real64)/16
            case(2)
               if (j>i) base(i,j)=real(mod(7*i+3*j,11)-5,real64)/16
            case(3)
               if (i>j) base(i,j)=real(mod(7*i+3*j,11)-5,real64)/16
            case(4)
               if (j==mod(i,n)+1) base(i,j)=real(i+1,real64)
            end select
         end do
         if (pattern/=4) base(i,i)=1+sum(abs(base(i,:)))
      end do
      a=base
      if (order==2) a=base(n:1:-1,:)
      if (scale==1) a=a*1e-6_real64
      if (scale==2) a=a*1e6_real64
      saved=a
      do i=1,n
         truth(i,:)=[1.0_real64,real((-1)**i*i,real64)/8,real(i*(n+1-i),real64)/4]
      end do
      b=0
      do r=1,3
         do i=1,n
            do j=1,n
               b(i,r)=b(i,r)+saved(i,j)*truth(j,r)
            end do
         end do
      end do
      bsave=b
      call lu_factor(a,ipvt=ipvt,lu=packed,l=l,u=u,p=p)
      if (any(a/=saved)) error stop 'factorization changed input'
      if (.not.all(ieee_is_finite(packed)).or..not.all(ieee_is_finite(l)).or. &
          .not.all(ieee_is_finite(u)).or..not.all(ieee_is_finite(p))) error stop 'nonfinite factors'
      if (size(ipvt)/=n.or.any(shape(packed)/=[n,n])) error stop 'factor output shape'
      if (any(ipvt<1).or.any(ipvt>n)) error stop 'pivot range'
      rows=[(i,i=1,n)]
      do i=1,n
         if (ipvt(i)<i) error stop 'LAPACK pivot range'
         tmp=rows(i); rows(i)=rows(ipvt(i)); rows(ipvt(i))=tmp
      end do
      if (any(ipvt/=[(i,i=1,n)])) pivoted=pivoted+1
      factor_error=0
      do i=1,n
         if (l(i,i)/=1) error stop 'nonunit L diagonal'
         do j=1,n
            if (j>i.and.l(i,j)/=0) error stop 'L not lower triangular'
            if (i>j.and.u(i,j)/=0) error stop 'U not upper triangular'
            if (p(i,j)/=real(merge(1,0,j==rows(i)),real64)) error stop 'pivot matrix convention'
            value=0
            do k=1,n
               value=value+l(i,k)*u(k,j)
            end do
            factor_error=max(factor_error,abs(value-saved(rows(i),j))/maxval(abs(saved)))
         end do
      end do
      worst_factor=max(worst_factor,factor_error)
      if (factor_error>2e-12_real64) error stop 'P*A versus L*U mismatch'
      packed_copy=packed
      do r=1,3
         x=solve_lu(packed,ipvt,b(:,r))
         call check_solution(x,truth(:,r),saved,bsave(:,r))
      end do
      many=solve_lu(packed,ipvt,b)
      if (any(shape(many)/=[n,3])) error stop 'matrix solution shape'
      do r=1,3
         call check_solution(many(:,r),truth(:,r),saved,bsave(:,r))
      end do
      if (any(b/=bsave).or.any(packed/=packed_copy)) error stop 'solve input modified'
      solves=solves+4; fixtures=fixtures+1
   end subroutine fixture
   subroutine check_solution(x,truth,a,b)
      real(real64), intent(in) :: x(:),truth(:),a(:,:),b(:)
      real(real64) :: error,residual,value,denominator
      integer :: i,j
      if (size(x)/=size(truth)) error stop 'vector solution shape'
      if (.not.all(ieee_is_finite(x))) error stop 'nonfinite solution'
      error=maxval(abs(x-truth)/(1+abs(truth)))
      denominator=maxval(sum(abs(a),dim=2))*maxval(abs(x))+maxval(abs(b))
      residual=0
      do i=1,size(x)
         value=-b(i)
         do j=1,size(x)
            value=value+a(i,j)*x(j)
         end do
         residual=max(residual,abs(value)/denominator)
      end do
      worst_solution=max(worst_solution,error); worst_residual=max(worst_residual,residual)
      if (error>2e-12_real64.or.residual>2e-12_real64) error stop 'known solution or residual mismatch'
      entries=entries+size(x)
   end subroutine check_solution
   subroutine singular(n,pattern)
      integer, intent(in) :: n,pattern
      real(real64) :: a(n,n),saved(n,n)
      real(real64), allocatable :: packed(:,:),l(:,:),u(:,:),p(:,:)
      integer(int32), allocatable :: ipvt(:)
      integer :: i
      a=0
      if (pattern==2.and.n>1) then
         do i=1,n
            a(i,i)=1
         end do
         a(n,:)=a(1,:)
      end if
      saved=a
      call lu_factor(a,ipvt=ipvt,lu=packed,l=l,u=u,p=p)
      if (any(a/=saved)) error stop 'singular input changed'
      if (.not.all(ieee_is_nan(packed)).or..not.all(ieee_is_nan(l)).or. &
          .not.all(ieee_is_nan(u)).or..not.all(ieee_is_nan(p))) error stop 'singular diagnostic missing'
      if (any(ipvt/=0)) error stop 'singular pivot sentinel missing'
      rejections=rejections+1
   end subroutine singular
end program checked_linalg_lu
