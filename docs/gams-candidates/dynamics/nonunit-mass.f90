! Independent API consumer; MIT: licenses/diagonal-response-drivers-MIT.txt.
module force_model
   use iso_fortran_env,only:wp=>real64
   implicit none
   type force_state
      integer::pattern=1,calls=0
   end type
contains
   function physical_force(w,n,pattern) result(f)
      real(wp),intent(in)::w
      integer,intent(in)::n,pattern
      complex(wp)::f(n)
      integer::i
      do i=1,n
         f(i)=cmplx(real(i,wp)*(1+0.1_wp*w),real(pattern,wp)*(0.25_wp*i-0.2_wp*w),wp)
      end do
   end function
   subroutine forcing(w,f,args)
      real(wp),intent(in)::w
      complex(wp),intent(out)::f(:)
      class(*),optional,intent(inout)::args
      if (.not.present(args)) error stop 'missing force state'
      select type(args)
      type is(force_state)
         args%calls=args%calls+1
         f=physical_force(w,size(f),args%pattern)
      class default
         error stop 'incorrect force state'
      end select
   end subroutine
end module

program main
   use force_model
   use dynamics,only:frf,frequency_response,modal_excite
   use ieee_arithmetic,only:ieee_is_finite
   implicit none
   real(wp),parameter::frequencies(*)=[0.0_wp,0.5_wp,1.0_wp,1.5_wp,2.0_wp,2.5_wp,3.0_wp,4.0_wp]
   real(wp),parameter::masses(*)=[1.0_wp,2.0_wp],alphas(*)=[0.1_wp,0.4_wp],betas(*)=[0.0_wp,0.05_wp]
   type(frf)::response
   type(force_state)::state
   procedure(modal_excite),pointer::callback
   real(wp),allocatable::mass(:,:),stiffness(:,:),q(:,:),lambda(:),modes(:),shapes(:,:)
   real(wp)::factor,alpha,beta,w,value,worst,norm,modal_error
   complex(wp),allocatable::f(:),expected(:)
   complex(wp)::coefficient
   integer::n,im,rotation,ia,ib,pattern,i,j,k,iw,fixtures,checks
   callback=>forcing
   fixtures=0; checks=0; worst=0
   do n=1,3
      allocate(mass(n,n),stiffness(n,n),q(n,n),lambda(n),f(n),expected(n))
      lambda=[(real(i*i,wp),i=1,n)]
      do im=1,size(masses)
         factor=masses(im); mass=0
         do i=1,n
            mass(i,i)=factor
         end do
         do rotation=1,2
            q=0
            do i=1,n
               q(i,i)=1
            end do
            if (rotation==2) then
               norm=real(sum([(i*i,i=1,n)]),wp)
               do j=1,n
                  do i=1,n
                     q(i,j)=q(i,j)-2*real(i*j,wp)/norm
                  end do
               end do
            end if
            stiffness=0
            do j=1,n
               do i=1,n
                  do k=1,n
                     stiffness(i,j)=stiffness(i,j)+factor*q(i,k)*lambda(k)*q(j,k)
                  end do
               end do
            end do
            do ia=1,size(alphas)
               alpha=alphas(ia)
               do ib=1,size(betas)
                  beta=betas(ib)
                  do pattern=1,2
                     state=force_state(pattern,0)
                     response=frequency_response(mass,stiffness,alpha,beta,frequencies,callback, &
                        modes=modes,modeshapes=shapes,args=state)
                     if (any(shape(response%responses)/=[8,n])) error stop 'response shape'
                     if (.not.all(ieee_is_finite(abs(response%responses)))) error stop 'nonfinite response'
                     if (state%calls/=8.or.state%pattern/=pattern) error stop 'force callback state'
                     if (any(response%frequency/=frequencies)) error stop 'frequency output'
                     modal_error=maxval(abs(modes-sqrt(lambda)))
                     if (modal_error>1e-12_wp) error stop 'known natural frequencies'
                     do iw=1,size(frequencies)
                        w=frequencies(iw); f=physical_force(w,n,pattern); expected=0
                        do k=1,n
                           coefficient=sum(q(:,k)*f)/cmplx(factor*(lambda(k)-w*w), &
                              w*factor*(alpha+beta*lambda(k)),wp)
                           expected=expected+q(:,k)*coefficient
                        end do
                        value=maxval(abs(response%responses(iw,:)-expected))/max(1.0_wp,maxval(abs(expected)))
                        if (value>1e-10_wp) then
                           print *, 'Mismatch n,mass,rotation,alpha,beta,force,w,error:', &
                              n,factor,rotation,alpha,beta,pattern,w,value
                           error stop 'closed-form harmonic response'
                        end if
                        worst=max(worst,value); checks=checks+n
                     end do
                     fixtures=fixtures+1
                  end do
               end do
            end do
         end do
      end do
      deallocate(mass,stiffness,q,lambda,f,expected)
   end do
   if (fixtures/=96.or.checks/=1536) error stop 'accounting'
   print '(a,i0,a,i0)', 'Harmonic response fixtures: ',fixtures,'; complex coordinate checks: ',checks
   print '(a,es12.4)', 'Maximum normalized response error: ',worst
   print '(a)', 'PASS dynamics-response-reference'
end program
