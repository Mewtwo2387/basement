program Hello
    implicit none
    character(len=32) :: name

    write(*, "(a)", advance="no") "What's your name? "
    read *, name
    print "(3a)", "Hello, ", trim(name), "!"
end program Hello
