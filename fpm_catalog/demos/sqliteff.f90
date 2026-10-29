program main
   use sqliteff
   use iso_varying_string, only: varying_string
   implicit none
   type(SqliteDatabase_t) :: db
   type(SqliteStatement_t) :: query
   type(varying_string) :: message, remaining
   double precision :: average
   call check(sqliteff_open(':memory:', db), SQLITE_OK)
   call check(sqliteff_exec(db, 'create table measurements(value real);' // &
      'insert into measurements values(2.0),(4.0),(6.0);', message), SQLITE_OK)
   call check(sqliteff_prepare(db, 'select count(*), avg(value) from measurements;', &
      query, remaining), SQLITE_OK)
   call check(sqliteff_step(query), SQLITE_ROW)
   if (sqliteff_column_int(query, 0) /= 3) error stop 'row count'
   average = sqliteff_column_double(query, 1)
   if (abs(average - 4.0d0) > 1.0d-12) error stop 'average'
   print '(a,f5.2)', 'Average of three measurements: ', average
   call check(sqliteff_step(query), SQLITE_DONE)
   call check(sqliteff_finalize(query), SQLITE_OK)
   call check(sqliteff_close(db), SQLITE_OK)
   print *, 'PASS sqliteff'
contains
   subroutine check(actual, expected)
      integer, intent(in) :: actual, expected
      if (actual /= expected) then
         print *, 'Unexpected SQLite status:', actual, ' expected:', expected
         error stop 'SQLite operation failed'
      end if
   end subroutine
end program
