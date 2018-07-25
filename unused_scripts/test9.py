try:
    print 'Hello'
    
    try:
        print 'Hello' + 2
    except:
        raise Failed    
    
except Failed:
    print 'Failed'
except Exception as e:
    print 'Some other exception.'
    print e
    