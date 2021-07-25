from app import app
from models import db, Provider


db.drop_all()
db.create_all()


"""insert into providers table most of the 5 largest networks in the US"""
verizon = Provider(name='Verizon', value='@vtext.com')
at_t = Provider(name='AT&T', value='@txt.att.net')
sprint = Provider(name='Sprint', value='@messaging.sprintpcs.com')
t_modile = Provider(name='T-Mobile', value='@tmomail.net')
u_s_cellular = Provider(name='U.S. Cellular', value='@email.uscc.net')

db.session.add_all([verizon, at_t, sprint, t_modile, u_s_cellular])
db.session.commit()