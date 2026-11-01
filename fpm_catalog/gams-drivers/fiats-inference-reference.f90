! Independent MIT-licensed driver; see licenses/inference-pairs-drivers-MIT.txt.
program reference_fiats_networks
   use inference_engine_m, only: inference_engine_t,tensor_t,rkind
   use julienne_string_m, only: string_t
   use, intrinsic :: iso_fortran_env, only: real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   character(len=7), parameter :: names(*)=[character(len=7) :: 'relu','sigmoid','swish']
   integer, allocatable :: nodes(:)
   integer :: architecture,act,pattern,bias_mode,l,i,j,sample,networks,calls,entries,replays
   real(real64) :: z,expected,error,max_error
   networks=0; calls=0; entries=0; replays=0; max_error=0
   do architecture=1,4
      call set_architecture(architecture)
      do act=1,size(names)
         do pattern=1,2
            do bias_mode=0,1
               block
                  type(inference_engine_t) :: network
                  type(tensor_t) :: input,output
                  real(rkind) :: weights(maxval(nodes),maxval(nodes),ubound(nodes,1))
                  real(rkind) :: biases(maxval(nodes),ubound(nodes,1)),x(nodes(0))
                  real(rkind), allocatable :: values(:),first(:)
                  real(real64) :: previous(maxval(nodes)),next(maxval(nodes))
                  weights=17; biases=17
                  do l=1,ubound(nodes,1)
                     do i=1,nodes(l)
                        biases(i,l)=0
                        if (bias_mode==1) then
                           biases(i,l)=real(i-2*l,rkind)/8
                           if (pattern==2) biases(i,l)=real(i-2*l,rkind)/9
                        end if
                        do j=1,nodes(l-1)
                           weights(i,j,l)=real(2*i-3*j+l,rkind)/8
                           if (pattern==2) weights(i,j,l)=real(2*i-3*j+l,rkind)/7
                        end do
                     end do
                  end do
                  network=inference_engine_t(metadata=[string_t('Fixed scalar references'), &
                     string_t('Playground'),string_t('2026-11-01'),string_t(trim(names(act))),string_t('false')], &
                     weights=weights,biases=biases,nodes=nodes)
                  if (network%num_inputs()/=nodes(0) .or. network%num_outputs()/=nodes(ubound(nodes,1))) &
                     error stop 'Fiats dimensions differ'
                  do sample=1,11
                     x=0
                     if (sample>=2 .and. sample<=nodes(0)+1) then
                        x(sample-1)=1
                     else if (sample>nodes(0)+1) then
                        do j=1,size(x)
                           x(j)=real(modulo(sample*(2*j+1),17)-8,rkind)/8
                        end do
                     end if
                     input=tensor_t(x); output=network%infer(input); values=output%values()
                     if (size(values)/=nodes(ubound(nodes,1))) error stop 'wrong output width'
                     if (.not.all(ieee_is_finite(values))) error stop 'nonfinite Fiats output'
                     previous=0; previous(1:size(x))=real(x,real64)
                     do l=1,ubound(nodes,1)
                        next=0
                        do i=1,nodes(l)
                           z=real(biases(i,l),real64)
                           do j=1,nodes(l-1)
                              z=z+real(weights(i,j,l),real64)*previous(j)
                           end do
                           next(i)=activate(z,act)
                        end do
                        previous=next
                     end do
                     do i=1,size(values)
                        expected=previous(i)
                        error=abs(real(values(i),real64)-expected)/(1+abs(expected))
                        if (error>5e-6_real64) error stop 'Fiats scalar multilayer reference differs'
                        max_error=max(max_error,error); entries=entries+1
                     end do
                     if (sample==1) first=values
                     calls=calls+1
                  end do
                  x=0; input=tensor_t(x); output=network%infer(input); values=output%values()
                  if (any(values/=first)) error stop 'Fiats repeated zero input differs'
                  calls=calls+1; replays=replays+size(values); networks=networks+1
               end block
            end do
         end do
      end do
      deallocate(nodes)
   end do
   print '(a,i0,a,i0)', 'Fiats fixed networks: ',networks,'; inference calls: ',calls
   print '(a,i0,a,i0)', 'Independent output references: ',entries,'; exact replay entries: ',replays
   print '(a,i0)', 'Native decimal precision: ',precision(0.0_rkind)
   print '(a,es14.5)', 'Maximum normalized multilayer error: ',max_error
   print '(a)', 'ReLU/sigmoid/swish apply to every connection, including output; default ranges are identity.'
   print '(a)', 'Fixed inference only; training, derivatives, model I/O and nonidentity ranges unverified.'
   print '(a)', 'PASS fiats-inference-reference'
contains
   subroutine set_architecture(which)
      integer, intent(in) :: which
      if (which<=3) then
         allocate(nodes(0:2))
      else
         allocate(nodes(0:3))
      end if
      select case(which)
      case(1)
         nodes=[1,2,1]
      case(2)
         nodes=[2,3,2]
      case(3)
         nodes=[3,2,1]
      case(4)
         nodes=[2,4,3,2]
      end select
   end subroutine
   real(real64) function activate(x,which) result(value)
      real(real64), intent(in) :: x
      integer, intent(in) :: which
      real(real64) :: sigmoid
      if (x>=0) then
         sigmoid=1/(1+exp(-x))
      else
         sigmoid=exp(x)/(1+exp(x))
      end if
      select case(which)
      case(1)
         value=max(0.0_real64,x)
      case(2)
         value=sigmoid
      case(3)
         value=x*sigmoid
      end select
   end function
end program
