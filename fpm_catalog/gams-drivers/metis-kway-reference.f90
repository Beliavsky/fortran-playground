! Independent API consumer; see licenses/products-partitions-drivers-MIT.txt.
program checked_graph_partitions
   use metis_c_interface
   implicit none
   integer, parameter :: sizes(3)=[12,24,48],seeds(3)=[1,42,93]
   integer(idx_t), allocatable :: weights(:,:),xadj(:),adjncy(:),adjwgt(:),part(:)
   integer(idx_t), allocatable :: saved_x(:),saved_adj(:),saved_w(:)
   integer(idx_t) :: options(0:METIS_NOPTIONS-1),nvtxs,ncon,nparts,edgecut,status,reference
   integer :: s,n,family,weighted,i,j,next,parts,seed,population,partition,calls=0,vertices=0
   integer :: smallest=huge(0),largest=0
   logical :: edge
   do s=1,3
      n=sizes(s); nvtxs=int(n,idx_t); ncon=1_idx_t
      allocate(weights(n,n),xadj(n+1),part(n))
      do family=1,3
         do weighted=1,2
            weights=0
            do i=1,n
               do j=i+1,n
                  select case(family)
                  case(1)
                     edge=j-i==1.or.j-i==n-1
                  case(2)
                     edge=(j-i==1.and.(i-1)/4==(j-1)/4).or.j-i==4
                  case(3)
                     edge=(i-1)/(n/3)==(j-1)/(n/3)
                     edge=edge.or.(j==i+1.and.modulo(i,n/3)==0)
                  end select
                  if (.not.edge) cycle
                  weights(i,j)=1_idx_t
                  if (weighted==2) weights(i,j)=int(1+modulo(3*i+5*j,7),idx_t)
                  weights(j,i)=weights(i,j)
               end do
            end do
            allocate(adjncy(count(weights/=0)),adjwgt(count(weights/=0)))
            next=1
            do i=1,n
               xadj(i)=int(next-1,idx_t)
               do j=1,n
                  if (weights(i,j)==0) cycle
                  adjncy(next)=int(j-1,idx_t); adjwgt(next)=weights(i,j); next=next+1
               end do
            end do
            xadj(n+1)=int(next-1,idx_t)
            saved_x=xadj; saved_adj=adjncy; saved_w=adjwgt
            do parts=2,3
               nparts=int(parts,idx_t)
               do seed=1,3
                  status=METIS_SetDefaultOptions(options)
                  if (status/=METIS_OK) error stop 'METIS defaults'
                  options(METIS_OPTION_SEED)=int(seeds(seed),idx_t)
                  ! Pinned Fortran NUMBERING/UFACTOR indices disagree with the bundled C enum.
                  ! Keep default zero-based numbering; supply the imbalance through the typed API.
                  status=METIS_PartGraphKway(nvtxs,ncon,xadj,adjncy,adjwgt=adjwgt,nparts=nparts, &
                     ubvec=[1.1_real_t],options=options,edgecut=edgecut,part=part)
                  if (status/=METIS_OK) error stop 'METIS kway status'
                  if (any(part<0).or.any(part>=nparts)) error stop 'invalid part number'
                  do partition=0,parts-1
                     population=count(part==partition)
                     if (population<1.or.2*population*parts>3*n) error stop 'partition population'
                     smallest=min(smallest,population); largest=max(largest,population)
                  end do
                  reference=0_idx_t
                  ! Count each undirected edge once from the original dense graph, not returned CSR.
                  do i=1,n
                     do j=i+1,n
                        if (part(i)/=part(j)) reference=reference+weights(i,j)
                     end do
                  end do
                  if (edgecut/=reference.or.edgecut<0) error stop 'independent weighted edge cut'
                  if (any(xadj/=saved_x).or.any(adjncy/=saved_adj).or.any(adjwgt/=saved_w)) &
                     error stop 'graph inputs changed'
                  calls=calls+1; vertices=vertices+n
               end do
            end do
            deallocate(adjncy,adjwgt,saved_x,saved_adj,saved_w)
         end do
      end do
      deallocate(weights,xadj,part)
   end do
   print '(a,i0)', 'K-way graph partitions: ',calls
   print '(a,i0)', 'Assigned vertices checked: ',vertices
   print '(a,i0)', 'Independent weighted-cut references: ',calls
   print '(a,2i6)', 'Smallest/largest observed part: ',smallest,largest
   print '(a)', 'PASS metis-kway-reference'
end program checked_graph_partitions
