def isprime(startnumber):
    """ 
    This function checks if a number is 
    prime or not. 
    """
    startnumber*=1.0
    for divisor in range(2,int(startnumber**0.5)+1):
        if startnumber/divisor==int(startnumber/divisor):
            return False
    return True
