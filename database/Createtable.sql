CREATE TABLE Farm (
    Farm_ID serial PRIMARY KEY,
    Farm_Name varchar(30) NOT NULL,
    Farm_Location varchar(50) NOT NULL
);

CREATE TABLE Cage (
    Cage_ID serial PRIMARY KEY,
    Farm_ID integer NOT NULL,
    Cage_Location varchar(50) NOT NULL,
    Cage_Name varchar(30) NOT NULL,

    CONSTRAINT fk_farm FOREIGN KEY (Farm_ID) REFERENCES Farm(Farm_ID)
    );

CREATE TABLE CageTimeLine (
    TimeLine_ID serial PRIMARY KEY,
    Cage_ID integer NOT NULL,
    Farm_ID integer NOT NULL,
    Stocking_Date timestamp NOT NULL,
    Harves_Date timestamp,

    CONSTRAINT fk_cage FOREIGN KEY (Cage_ID) REFERENCES Cage (Cage_ID),
    CONSTRAINT fk_farm FOREIGN KEY (Farm_ID) REFERENCES Farm (Farm_ID)
    );

CREATE TABLE Fish (
    Fish_ID serial PRIMARY KEY,
    Cage_ID integer NOT NULL,
    Farm_ID integer NOT NULL,
    TimeLine_ID integer NOT NULL,
    Image_Path text NOT NULL,
    Capture_Date timestamp NOT NULL,
    Weight numeric(5,2),
    Length numeric(5,2),
    Lice_Adult_Female integer,
    Lice_Mobility integer,
    Lice_Attached integer,

    CONSTRAINT fk_cage FOREIGN KEY (Cage_ID) REFERENCES Cage (Cage_ID),
    CONSTRAINT fk_farm FOREIGN KEY (Farm_ID) REFERENCES Farm (Farm_ID),
    CONSTRAINT fk_timeline FOREIGN KEY (TimeLine_ID) REFERENCES CageTimeLine (TimeLine_ID)
);
