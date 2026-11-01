! Independent MIT-licensed driver; see licenses/radial-dense-drivers-MIT.txt.
program reference_dense_layers
   use athena, only: full_layer_type,array_type
   use, intrinsic :: iso_fortran_env, only: real32,real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: inputs(*)=[1,2,3,5],outputs(*)=[1,2,4]
   character(len=7), parameter :: activations(*)=[character(len=7) :: 'none','relu','tanh','sigmoid']
   integer :: ni,no,ii,oo,act,bias_mode,pattern,sample,i,j,layers,calls,entries,replays
   real(real64) :: z,expected,error,max_error
   layers=0; calls=0; entries=0; replays=0; max_error=0
   do ii=1,size(inputs)
      ni=inputs(ii)
      do oo=1,size(outputs)
         no=outputs(oo)
         do act=1,size(activations)
            do bias_mode=0,1
               do pattern=1,2
                  block
                     type(full_layer_type) :: layer
                     type(array_type) :: feature(1,1)
                     real(real32) :: w(no,ni),b(no),x(ni,1),first_prediction(no),first_x(ni)
                     layer=full_layer_type(num_inputs=ni,num_outputs=no,use_bias=bias_mode==1, &
                        activation=trim(activations(act)))
                     do j=1,ni
                        do i=1,no
                           w(i,j)=real(2*i-3*j+1,real32)/8
                           if (pattern==2) w(i,j)=real(2*i-3*j+1,real32)/7
                        end do
                     end do
                     do i=1,no
                        b(i)=real(2*i-3,real32)/8
                        if (pattern==2) b(i)=real(2*i-3,real32)/9
                     end do
                     layer%params(1)%val(:,1)=reshape(w,[no*ni])
                     if (bias_mode==1) layer%params(2)%val(:,1)=b
                     x=0
                     call feature(1,1)%allocate(source=x)
                     ! This named input is reused; it is not an owned expression temporary.
                     feature(1,1)%is_temporary=.false.
                     do sample=1,11
                        x=0
                        if (sample>=2 .and. sample<=ni+1) then
                           x(sample-1,1)=1
                        else if (sample>ni+1) then
                           do j=1,ni
                              x(j,1)=real(modulo(sample*(2*j+1),17)-8,real32)/8
                           end do
                        end if
                        feature(1,1)%val(:,1)=x(:,1)
                        call layer%forward(feature)
                        if (size(layer%output(1,1)%val)/=no) error stop 'wrong output dimensions'
                        if (.not.all(ieee_is_finite(layer%output(1,1)%val))) error stop 'nonfinite dense output'
                        do i=1,no
                           z=0
                           if (bias_mode==1) z=real(b(i),real64)
                           do j=1,ni
                              z=z+real(w(i,j),real64)*real(x(j,1),real64)
                           end do
                           expected=activate(z,act)
                           error=abs(real(layer%output(1,1)%val(i,1),real64)-expected)/(1+abs(expected))
                           if (error>2e-6_real64) error stop 'independent scalar dense reference differs'
                           max_error=max(max_error,error); entries=entries+1
                        end do
                        if (sample==1) then
                           first_prediction=layer%output(1,1)%val(:,1); first_x=x(:,1)
                        end if
                        calls=calls+1
                     end do
                     ! Revisit the initial feature after other forward calls to expose stale state.
                     feature(1,1)%val(:,1)=first_x
                     call layer%forward(feature)
                     if (any(layer%output(1,1)%val(:,1)/=first_prediction)) error stop 'repeated forward differs'
                     calls=calls+1; replays=replays+no; layers=layers+1
                  end block
               end do
            end do
         end do
      end do
   end do
   print '(a,i0,a,i0)', 'Fixed dense layers: ',layers,'; forward calls: ',calls
   print '(a,i0,a,i0)', 'Independent output references: ',entries,'; exact replay entries: ',replays
   print '(a,es14.5)', 'Maximum normalized output error against real64 scalar oracle: ',max_error
   print '(a)', 'Four activations, bias on/off, rectangular weights, zero/basis/mixed inputs and repeated forward checked.'
   print '(a)', 'Inference only; training, automatic derivatives, batch inference and approximation quality unverified.'
   print '(a)', 'PASS athena-dense-reference'
contains
   real(real64) function activate(x,kind) result(value)
      real(real64), intent(in) :: x
      integer, intent(in) :: kind
      select case(kind)
      case(1)
         value=x
      case(2)
         value=max(0.0_real64,x)
      case(3)
         value=2/(1+exp(-2*x))-1
      case(4)
         if (x>=0) then
            value=1/(1+exp(-x))
         else
            value=exp(x)/(1+exp(x))
         end if
      case default
         error stop 'unknown reference activation'
      end select
   end function
end program
