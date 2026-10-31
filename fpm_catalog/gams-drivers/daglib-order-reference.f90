! Independent API consumer; MIT: licenses/graph-neighbors-drivers-MIT.txt.
program main
   use dag_module,only:dag,ip=>daglib_ip
   implicit none
   type(dag)::graph
   integer(ip),allocatable::order(:)
   integer(ip)::labels(5),parents(5),status
   logical::dependency(5,5)
   integer::labeling,mask,child,parent,bit,k,i,n,repeat,cycle_size
   integer::graphs,sort_calls,rejected,edge_checks
   graphs=0; sort_calls=0; rejected=0; edge_checks=0
   n=5
   do labeling=1,2
      labels=[1_ip,2_ip,3_ip,4_ip,5_ip]
      if (labeling==2) labels=labels(5:1:-1)
      do mask=0,1023
         call graph%set_vertices(5_ip)
         dependency=.false.; bit=0
         do child=2,5
            k=0
            do parent=1,child-1
               if (btest(mask,bit)) then
                  k=k+1; parents(k)=labels(parent)
                  dependency(labels(child),labels(parent))=.true.
               end if
               bit=bit+1
            end do
            if (k>0) call graph%set_edges(labels(child),parents(:k))
         end do
         do repeat=1,2
            call verify()
         end do
         graphs=graphs+1
         call graph%destroy()
         if (graph%number_of_vertices()/=0) error stop 'graph destruction'
      end do
   end do
   do cycle_size=1,3
      call graph%set_vertices(int(cycle_size,ip))
      do i=1,cycle_size
         call graph%set_edges(int(i,ip),[int(mod(i,cycle_size)+1,ip)])
      end do
      do repeat=1,2
         call graph%toposort(order,status)
         if (status/=-1.or.allocated(order)) error stop 'cycle status/output'
         rejected=rejected+1
      end do
      ! Rebuild the same object after a failed sort and verify a known chain.
      n=3; dependency=.false.
      call graph%set_vertices(3_ip)
      call graph%set_edges(2_ip,[1_ip]); dependency(2,1)=.true.
      call graph%set_edges(3_ip,[2_ip]); dependency(3,2)=.true.
      do repeat=1,2
         call verify()
      end do
      graphs=graphs+1
      call graph%destroy()
   end do
   if (graphs/=2051.or.sort_calls/=4102.or.rejected/=6.or.edge_checks/=20492) error stop 'accounting'
   print '(a,i0,a,i0)', 'Acyclic graph fixtures: ',graphs,'; valid topological sorts: ',sort_calls
   print '(a,i0)', 'Independent dependency precedence checks: ',edge_checks
   print '(a,i0)', 'Expected cyclic rejections: ',rejected
   print '(a)', 'Permutation integrity, repeated sorting, explicit cycle status and object recovery.'
   print '(a)', 'PASS daglib-order-reference'
contains
   subroutine verify()
      integer::i,j,positions(5)
      call graph%toposort(order,status)
      if (status/=0) error stop 'acyclic sort status'
      if (.not.allocated(order)) error stop 'unallocated order'
      if (size(order)/=n.or.any(order<1).or.any(order>n)) error stop 'order shape/range'
      positions=0
      do i=1,n
         if (count(order==i)/=1) error stop 'order permutation'
         positions(order(i))=i
      end do
      do i=1,n
         do j=1,n
            if (.not.dependency(i,j)) cycle
            if (positions(j)>=positions(i)) error stop 'dependency precedence'
            edge_checks=edge_checks+1
         end do
      end do
      sort_calls=sort_calls+1
   end subroutine
end program
