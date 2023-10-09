import datetime
from sqlalchemy import create_engine, and_, distinct, func
from sqlalchemy.orm import sessionmaker
from database_orm import *
import pandas as pd

engine = create_engine('postgresql+psycopg2://postgres:public@localhost/farm_management')
Session = sessionmaker(bind=engine)
session = Session()

def get_days_in_week(year, week_number):
    # Create a date for the first day of the year
    start_date = datetime.date(year, 1, 1)
    
    # Calculate the number of days to add to reach the desired week
    days_to_add = week_number * 7 - start_date.weekday() # Monday
    
    # Calculate the first day of the desired week
    week_start_date = start_date + datetime.timedelta(days=days_to_add)
    # Create a list to store the days of the week
    week_days = []
    # Iterate through the week and add each day to the list
    for i in range(7):
        day = week_start_date + datetime.timedelta(days=i)
        week_days.append(day)
    
    return week_days

def get_date(date_time):
    return date_time.date()

def get_cage_by_farm(farm_id):
    query = session.query(Cage).filter(Cage.farm_id==farm_id).distinct(Cage.cage_location).all()
    df_cage = pd.DataFrame([(r.cage_id, r.farm_id, r.cage_location, r.cage_name) for r in query], 
                        columns=['cage_id', 'farm_id', 'cage_location', 'cage_name'])
    return df_cage

def get_cageid_by_name(cage_name):
    cage_id = session.query(Cage).filter(Cage.cage_name==cage_name).one().cage_id
    return cage_id

def get_cage_by_cage_location(cage_location):
    query = session.query(Cage).filter(Cage.cage_location==cage_location).all()
    df_cage = pd.DataFrame([(r.cage_id, r.farm_id, r.cage_location, r.cage_name) for r in query], 
                        columns=['cage_id', 'farm_id', 'cage_location', 'cage_name'])
    return df_cage

def get_fish_by_week_and_cage(week, cage_id):
    days = get_days_in_week(2023, int(week))
    start_date = days[0]
    end_date = days[-1] + datetime.timedelta(days=1)
    # Query and group by the date part of capture_date
    result = session.query(
        func.DATE(Fish.capture_date).label("capture_date"),
        func.count().label("fish_count"),
        func.sum(Fish.lice_adult_female).label("lice_adult_female_sum"),
        func.sum(Fish.lice_mobility).label("lice_mobility_sum"),
        func.sum(Fish.lice_attached).label("lice_attached_sum"),
        func.sum(Fish.lice_attached + Fish.lice_adult_female + Fish.lice_mobility).label("lice_total")
    ).filter(and_(
        Fish.capture_date >= start_date,
        Fish.capture_date <= end_date,
        Fish.cage_id == cage_id)
    ).group_by(
        func.DATE(Fish.capture_date)
    ).all()

    # Convert the result to dataframe
    df_fish = pd.DataFrame([(row.capture_date,
                            row.fish_count,
                            row.lice_adult_female_sum,
                            row.lice_mobility_sum,
                            row.lice_attached_sum,
                            row.lice_total)
                        for row in result],
                        columns=["CaptureDate",
                                "FishCount",
                                "LiceAdultFemaleSum",
                                "LiceMobilitySum",
                                "LiceAttachedSum",
                                "LiceTotal"
                                ])
    
    return df_fish

def get_fish_nolice_by_date(target_farm_id, target_cage_id, target_date):
    print(target_date)
    # Query the fish meeting the specified criteria
    fish_with_zero_lice = session.query(Fish).filter(
        and_(
            func.DATE(Fish.capture_date) == target_date,
            Fish.farm_id == target_farm_id,
            Fish.cage_id == target_cage_id,
            (Fish.lice_adult_female + Fish.lice_mobility + Fish.lice_attached) == 0
        )
    ).all()

    df_fish = pd.DataFrame([(fish.fish_id,
                        fish.cage_id,
                        fish.farm_id,
                        fish.timeline_id,
                        fish.image_path,
                        fish.capture_date,
                        fish.weight,
                        fish.length,
                        fish.lice_adult_female,
                        fish.lice_mobility,
                        fish.lice_attached)
                    for fish in fish_with_zero_lice],
                    columns=["FishID",
                            "CageID",
                            "FarmID",
                            "TimelineID",
                            "ImagePath",
                            "CaptureDate",
                            "Weight",
                            "Length",
                            "LiceAdultFemale",
                            "LiceMobility",
                            "LiceAttached"])
    
    return df_fish

def get_fish_lice_by_date(target_farm_id, target_cage_id, target_date):
    print(target_date)
    # Query the fish meeting the specified criteria
    fish_with_zero_lice = session.query(Fish).filter(
        and_(
            func.DATE(Fish.capture_date) == target_date,
            Fish.farm_id == target_farm_id,
            Fish.cage_id == target_cage_id,
            (Fish.lice_adult_female + Fish.lice_mobility + Fish.lice_attached) != 0
        )
    ).all()

    df_fish = pd.DataFrame([(fish.fish_id,
                        fish.cage_id,
                        fish.farm_id,
                        fish.timeline_id,
                        fish.image_path,
                        fish.capture_date,
                        fish.weight,
                        fish.length,
                        fish.lice_adult_female,
                        fish.lice_mobility,
                        fish.lice_attached)
                    for fish in fish_with_zero_lice],
                    columns=["FishID",
                            "CageID",
                            "FarmID",
                            "TimelineID",
                            "ImagePath",
                            "CaptureDate",
                            "Weight",
                            "Length",
                            "LiceAdultFemale",
                            "LiceMobility",
                            "LiceAttached"])
    
    return df_fish