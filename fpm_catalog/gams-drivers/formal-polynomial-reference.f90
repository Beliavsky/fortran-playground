! Independent API consumer; see licenses/periodic-calculus-drivers-MIT.txt.
module polynomial_fields
   implicit none
   integer :: p=0,q=0
   real :: origin=0,length=1
contains
   pure function scalar_field(x) result(f)
      real, intent(in) :: x(:)
      real, allocatable :: f(:)
      f=((x-origin)/length)**p
   end function scalar_field
   pure function vector_field(x) result(v)
      real, intent(in) :: x(:)
      real, allocatable :: v(:)
      v=((x-origin)/length)**q
   end function vector_field
end module polynomial_fields
program checked_formal_polynomials
   use formal_m, only: scalar_1D_t,vector_1D_t,gradient_1D_t,divergence_1D_t, &
      scalar_1D_initializer_i,vector_1D_initializer_i
   use polynomial_fields
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   procedure(scalar_1D_initializer_i), pointer :: fs=>scalar_field
   procedure(vector_1D_initializer_i), pointer :: vs=>vector_field
   integer, parameter :: grids(3)=[32,64,128]
   real, parameter :: origins(3)=[-1.5,0.0,0.75],lengths(3)=[1.0,0.5,2.0]
   integer :: order,grid,domain,fixtures=0,derivatives=0,integrals=0
   real :: worst_derivative=0,worst_quadrature=0,worst_conservation=0
   do order=2,4,2
      do grid=1,3
         do domain=1,3
            origin=origins(domain); length=lengths(domain)
            do p=0,2
               do q=0,2
                  call fixture(order,grids(grid))
               end do
            end do
         end do
      end do
   end do
   print '(a,i0)', 'Polynomial field pairs: ',fixtures
   print '(a,i0)', 'Pointwise derivative references: ',derivatives
   print '(a,i0)', 'Analytic integral references: ',integrals
   print '(a,es12.4)', 'Maximum normalized derivative error: ',worst_derivative
   print '(a,es12.4)', 'Maximum analytic integral error: ',worst_quadrature
   print '(a,es12.4)', 'Maximum conservation residual: ',worst_conservation
   print '(a)', 'PASS formal-polynomial-reference'
contains
   subroutine fixture(order,n)
      integer, intent(in) :: order,n
      type(scalar_1D_t) :: f
      type(vector_1D_t) :: v
      type(gradient_1D_t) :: gradient
      type(divergence_1D_t) :: divergence
      real, allocatable :: x(:),values(:),reference(:)
      real :: error,vg,fd,boundary,vg_ref,fd_ref,bound_ref,quadrature_bound
      f=scalar_1D_t(fs,order,n,origin,origin+length)
      v=vector_1D_t(vs,order,n,origin,origin+length)
      gradient=.grad.f; divergence=.div.v
      x=gradient%grid(); values=gradient%values(); allocate(reference(size(x)))
      reference=0
      if (p>0) reference=real(p)*((x-origin)/length)**(p-1)/length
      call check_derivative(values,reference)
      deallocate(reference)
      x=divergence%grid(); values=divergence%values(); allocate(reference(size(x)))
      reference=0
      if (q>0) reference=real(q)*((x-origin)/length)**(q-1)/length
      call check_derivative(values,reference)
      vg=.SSS.(v .dot. .grad.f)*f%dV()
      fd=.SSS.(f*.div.v)*f%dV()
      boundary=.SS.(f .x. (v .dot. v%dA()))
      vg_ref=0; fd_ref=0; bound_ref=0
      if (p+q>0) then
         vg_ref=real(p)/real(p+q); fd_ref=real(q)/real(p+q); bound_ref=1
      end if
      if (.not.all(ieee_is_finite([vg,fd,boundary]))) error stop 'nonfinite integral'
      error=max(abs(vg-vg_ref),abs(fd-fd_ref),abs(boundary-bound_ref))
      quadrature_bound=2e-4
      if (order==2) quadrature_bound=quadrature_bound+2.0/real(n*n)
      worst_quadrature=max(worst_quadrature,error)
      worst_conservation=max(worst_conservation,abs(vg+fd-boundary))
      if (error>quadrature_bound) error stop 'analytic integral mismatch'
      if (abs(vg+fd-boundary)>5e-4) error stop 'mimetic conservation mismatch'
      integrals=integrals+3; fixtures=fixtures+1
   end subroutine fixture
   subroutine check_derivative(values,reference)
      real, intent(in) :: values(:),reference(:)
      real :: error
      if (size(values)/=size(reference)) error stop 'derivative grid shape'
      if (.not.all(ieee_is_finite(values))) error stop 'nonfinite derivative'
      error=maxval(abs(values-reference)/(1+abs(reference)))
      worst_derivative=max(worst_derivative,error)
      if (error>5e-4) error stop 'polynomial derivative mismatch'
      derivatives=derivatives+size(values)
   end subroutine check_derivative
end program checked_formal_polynomials
