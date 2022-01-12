from nipype.interfaces import fsl
from nipype.pipeline import Node, MapNode
from nipype.interfaces import Function


def infile_to_outfile(**kwargs):
    return kwargs['in_file']


def extraction_node(config: dict, **kwargs):
    '''
    Parses config file to return desired brain extraction method.
    Parameters
    ----------
    config : dict
        PALS config file
    kwargs
        Keyword arguments to send to brain extraction method.

    Returns
    -------
    MapNode
    '''
    # Get extraction type
    extract_type = config['Analysis']['BrainExtractionMethod']
    if(not config['Analysis']['BrainExtraction']):
        # No brain extraction; in-> out
        n = MapNode(Function(function=infile_to_outfile, input_names='in_file', output_names='out_file'),
                    name='extract_skip', iterfield='in_file')
        return n
    elif(extract_type.lower() == 'bet'):
        n = MapNode(fsl.BET(**kwargs), name='extraction_bet', iterfield='in_file')
        return n
    else:
        raise(NotImplementedError(f'Extraction method {extract_type} not implemented.'))


def registration_node(config: dict, **kwargs):
    '''
    Parses config file to return desired registration method.
    Parameters
    ----------
    config : dict
        PALS config file
    kwargs
        Keyword arguments to send to registration method.

    Returns
    -------
    MapNode
    '''
    # Get registration method
    reg_method = config['Analysis']['RegistrationMethod']
    if(not config['Analysis']['Registration']):
        # No registration; in -> out
        n = MapNode(Function(function=infile_to_outfile, input_names='in_file',
                             output_names=['out_file', 'out_matrix_file']),
                    name='registration_skip', iterfield='in_file')
    elif(reg_method.lower() == 'flirt'):
        # Use FLIRT
        n = MapNode(fsl.FLIRT(**kwargs), name='registration_flirt', iterfield='in_file')
    else:
        raise(NotImplementedError(f'Registration method {reg_method} not implemented.'))
    return n


def apply_xfm_node(config: dict, **kwargs):
    '''
    Parses config file to return desired apply_xfm node.
    Parameters
    ----------
    config : dict
        PALS config file
    kwargs
        Keyword arguments to send to registration method.

    Returns
    -------
    MapNode
    '''

    if(not config['Analysis']['Registration']):
        # No registration; no xfm to apply.
        n = MapNode(Function(function=infile_to_outfile,
                             input_names=['in_file', 'in_matrix_file'],
                             output_names='out_file'),
                    name='transformation_skip', iterfield=['in_file', 'in_matrix_file'])
    else:
        n = MapNode(fsl.FLIRT(apply_xfm=True, reference=config['Template']),
                    name='transformation_flirt', iterfield=['in_file', 'in_matrix_file'])
    return n
