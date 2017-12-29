def fizz(num):
    response = ""
    for n in range(1, num + 1):
        response += buzz(n)
    return response


def buzz(n):
    if n % 3 == 0 and n % 5 == 0:
        return ', Fizz-Buzz'
    elif n % 3 == 0:
        return ', Fizz'
    elif n % 5 == 0:
        return ', Buzz'
    else:
        response = ", "
        response += str(n)
        return response
