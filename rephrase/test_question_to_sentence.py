import include_sys_path
import unittest

from rephrase.question_to_sentence import QTS
from rephrase.settings import USE_QTS_CACHE

include_sys_path.void()


class QTSTest(unittest.TestCase):

    def setUp(self):
        if USE_QTS_CACHE:
            print("Warning! QTS cache is enabled!")

    def tearDown(self):
        pass

    def test_which_of(self):
        self.assertEqual(
            QTS.process("Which of these is a greenhouse gas?"),
            "@placeholder is a greenhouse gas ."
        )
        self.assertEqual(
            QTS.process("Which of the following cars is the most "
                        "expensive car?"),
            "@placeholder is the most expensive car ."
        )
        self.assertEqual(
            QTS.process("Which of these practices would best support a claim "
                        "that an experiment led to a scientific discovery?"),
            "@placeholder would best support a claim that an experiment "
            "led to a scientific discovery ."
        )
        self.assertEqual(
            QTS.process("Which of these uses sound waves to locate "
                        "underwater objects?"),
            "@placeholder uses sound waves to locate underwater objects ."
        )
        self.assertEqual(
            QTS.process("Do you like pets? Yes, I do, indeed! "
                        "Which of these is a freshwater reservoir ?"),
            "Do you like pets? Yes, I do, indeed! "
            "@placeholder is a freshwater reservoir ."
        )
        self.assertEqual(
            QTS.process("Which of Alexanders commanders were the first to "
                        "visit Bahrain?"),
            "@placeholder were the first to visit Bahrain ."
        )
        self.assertEqual(
            QTS.process("Which of Darwin's books featured a plant whose "
                        "elaborate structure aided with fertilization "
                        "by insects?"),
            "@placeholder featured a plant whose elaborate structure aided "
            "with fertilization by insects ."
        )
        self.assertEqual(
            QTS.process("Which of the Tuvalu isalnds did de Peyster see?"),
            "@placeholder did de Peyster see ."
        )
        self.assertEqual(
            QTS.process("Which of the seven P&O cruise liners has a name "
                        "that begins with V?"),
            "@placeholder has a name that begins with V ."
        )
        self.assertEqual(
            QTS.process("Which of two can be more efficiently electricified"),
            "@placeholder can be more efficiently electricified ."
        )

    def test_in_which_of(self):
        self.assertEqual(
            QTS.process("In which of these investigations would pictures from "
                        "a camera be most useful?"),
            "pictures from a camera be most useful in @placeholder ."
        )
        self.assertEqual(
            QTS.process("In which of these investigations would pictures from "
                        "a camera be most useful"),
            "pictures from a camera be most useful in @placeholder ."
        )
        self.assertEqual(
            QTS.process("In which of these investigations would pictures from "
                        "a camera be most useful???"),
            "pictures from a camera be most useful in @placeholder ."
        )
        self.assertEqual(
            QTS.process("In which of these investigations would pictures from "
                        "a camera be most useful.?!"),
            "pictures from a camera be most useful in @placeholder ."
        )
        self.assertEqual(
            QTS.process("In which of these investigations would pictures from "
                        "a camera be most useful."),
            "pictures from a camera be most useful in @placeholder ."
        )
        self.assertEqual(
            QTS.process("In which of these investigations pictures from "
                        "a camera would be most useful?"),
            "pictures from a camera would be most useful in @placeholder ."
        )
        self.assertEqual(
            QTS.process("In which of the following types of cells does "
                        "cellular respiration occur?"),
            "cellular respiration occur in @placeholder ."
        )
        self.assertEqual(
            QTS.process("I like bananas. in which of the following types of "
                        "cells does cellular respiration occur?"),
            "I like bananas. cellular respiration occur in @placeholder ."
        )
        self.assertEqual(
            QTS.process("In which of Einstein's two theories do time and "
                        "space merge into spacetime?"),
            "time and space merge into spacetime in @placeholder ."
        )
        self.assertEqual(
            QTS.process("That's a very nice 2nd goal! In which of the "
                        "Einstein's two theories do time and space merge "
                        "into spacetime?"),
            "That's a very nice 2nd goal! time and space merge into "
            "spacetime in @placeholder ."
        )

    def test_replace_underscores(self):
        self.assertEqual(
            QTS.process("The atoms in a can of soda are __________."),
            "The atoms in a can of soda are @placeholder."
        )
        self.assertEqual(
            QTS.process("The atoms in a can of soda are ________"),
            "The atoms in a can of soda are @placeholder"
        )
        self.assertEqual(
            QTS.process("Wow! Nice match. The atoms in a can of soda "
                        "are __________."),
            "Wow! Nice match. The atoms in a can of soda are @placeholder."
        )
        self.assertEqual(
            QTS.process("The atoms in a can of soda are ___________!"),
            "The atoms in a can of soda are @placeholder!"
        )
        self.assertEqual(
            QTS.process("The atoms in a can of soda are __________?"),
            "The atoms in a can of soda are @placeholder?"
        )
        self.assertEqual(
            QTS.process("When two or more different elements are combined, "
                        "a(n) __________ is formed."),
            "When two or more different elements are combined, "
            "a(n) @placeholder is formed."
        )
        self.assertEqual(
            QTS.process("The place on a child's abdomen where the umbilical "
                        "cord was attached is called the ________, "
                        "or navel."),
            "The place on a child's abdomen where the umbilical cord was "
            "attached is called the @placeholder, or navel."
        )
        self.assertEqual(
            QTS.process("Mitochondria are to cellular respiration as "
                        "__________ are to photosynthesis."),
            "Mitochondria are to cellular respiration as @placeholder are "
            "to photosynthesis."
        )
        self.assertEqual(
            QTS.process("What are you talking about __ ? "
                        "Mitochondria are to cellular respiration as "
                        "__________ are to photosynthesis."),
            "What are you talking about __ ? "
            "Mitochondria are to cellular respiration as @placeholder are "
            "to photosynthesis."
        )
        self.assertEqual(
            QTS.process("The __ atoms in a can of soda are ________"),
            "The __ atoms in a can of soda are @placeholder"
        )
        self.assertEqual(
            QTS.process("The atoms in a __ can of soda are ________"),
            "The atoms in a __ can of soda are @placeholder"
        )
        self.assertEqual(
            QTS.process("The atoms __ in a can of soda __ are ________"),
            "The atoms __ in a can of soda __ are @placeholder"
        )

    def test_what_be(self):
        self.assertEqual(
            QTS.process("What is an example of a natural satellite?"),
            "An example of a natural satellite is @placeholder ."
        )
        self.assertEqual(
            QTS.process("What is an example of a natural satellite."),
            "An example of a natural satellite is @placeholder ."
        )
        self.assertEqual(
            QTS.process("What is an example of a natural satellite!"),
            "An example of a natural satellite is @placeholder ."
        )
        self.assertEqual(
            QTS.process("What is an example of a natural satellite"),
            "An example of a natural satellite is @placeholder ."
        )
        self.assertEqual(
            QTS.process("What are the reproductive cells produced by "
                        "the female reproductive organs called?"),
            "The reproductive cells produced by the female reproductive "
            "organs called are @placeholder ."
        )
        self.assertEqual(
            QTS.process("What are petri dishes used for in a lab?"),
            "Petri dishes used for in a lab are @placeholder ."
        )
        self.assertEqual(
            QTS.process("What is the primary job of red blood cells?"),
            "The primary job of red blood cells is @placeholder ."
        )
        self.assertEqual(
            QTS.process("What is the main source of energy that drives all "
                        "weather patterns ?"),
            "The main source of energy that drives all weather "
            "patterns is @placeholder ."
        )
        self.assertEqual(
            QTS.process("What is the primary function of skin cells !"),
            "The primary function of skin cells is @placeholder ."
        )
        self.assertEqual(
            QTS.process("What is involved in creating genetically "
                        "modified bacteria ?"),
            "Involved in creating genetically modified "
            "bacteria is @placeholder ."
        )
        self.assertEqual(
            QTS.process("What are those? "
                        "What is involved in creating genetically "
                        "modified bacteria ?"),
            "What are those? "
            "Involved in creating genetically modified "
            "bacteria is @placeholder ."
        )

    def test_what_do(self):
        self.assertEqual(
            QTS.process("What does vastenavond mean?"),
            "Vastenavond mean @placeholder ."
        )
        self.assertEqual(
            QTS.process("What does vastenavond mean!"),
            "Vastenavond mean @placeholder ."
        )
        self.assertEqual(
            QTS.process("What does vastenavond mean"),
            "Vastenavond mean @placeholder ."
        )
        self.assertEqual(
            QTS.process("What does vastenavond mean??"),
            "Vastenavond mean @placeholder ."
        )
        self.assertEqual(
            QTS.process("What does vastenavond mean??"),
            "Vastenavond mean @placeholder ."
        )
        self.assertEqual(
            QTS.process("What does an herbivore eat?"),
            "An herbivore eat @placeholder ."
        )
        self.assertEqual(
            QTS.process("What do plant roots prevent?!"),
            "Plant roots prevent @placeholder ."
        )
        self.assertEqual(
            QTS.process("What does Artharian legend claim about Glastonbury?"),
            "Artharian legend claim about Glastonbury @placeholder ."
        )
        self.assertEqual(
            QTS.process("What does FIFA stand for?"),
            "FIFA stand for @placeholder ."
        )
        self.assertEqual(
            QTS.process("What does the process of dielectric absorption "
                        "in a capacitor depend on?"),
            "The process of dielectric absorption in a capacitor "
            "depend on @placeholder ."
        )
        self.assertEqual(
            QTS.process("What does the line integral of the electric field "
                        "between the plates of a capacitor represent?"),
            "The line integral of the electric field between the plates "
            "of a capacitor represent @placeholder ."
        )
        self.assertEqual(
            QTS.process("What does Nyaya say causes human suffering?"),
            "Nyaya say causes human suffering @placeholder ."
        )

    def test_where_be(self):
        self.assertEqual(
            QTS.process("Where is the neural connection that is active "
                        "during migration located?"),
            "The neural connection that is active during migration "
            "is located in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where was the military Ocean Terminal Sunny "
                        "Point stationed?."),
            "The military Ocean Terminal Sunny Point was stationed "
            "in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where is work that has been sent up for "
                        "good stored?"),
            "Work that has been sent up for good is stored in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where was the relay event held in South Korea?"),
            "The relay event held in South Korea was in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where are HTS teams working with the military in "
                        "addition to Afghanistan?"),
            "HTS teams working with the military in addition to Afghanistan "
            "are in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where are the headquarters of the Congregation of "
                        "the Holy Cross?"),
            "The headquarters of the Congregation of the Holy Cross "
            "are in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where was the only place the Olympic torch was "
                        "carried in the Middle East?"),
            "The only place the Olympic torch was carried in the Middle "
            "East was in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where is the location of the original Olympic "
                        "events?"),
            "The location of the original Olympic events is in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where was Adolf Hitlers base of operation during "
                        "World War 2?"),
            "Adolf Hitlers base of operation during World War 2 "
            "was in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where were the Winter Olympics held in 1936?"),
            "The Winter Olympics held in 1936 were in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where were the piratical kingdoms from?"),
            "The piratical kingdoms were from @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where was their court in Kuaiji removed to?"),
            "Their court in Kuaiji was removed to @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where was Chopin's father from!"),
            "Chopin 's father was from @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where are the finals broadcast from?"),
            "The finals are broadcast from @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where were consumers going to buy devices other "
                        "than online?"),
            "Consumers were going to buy devices other than "
            "online in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where is sea surface temperature the highest?"),
            "Sea surface temperature is the highest in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where is sea surface temperature the highest?"),
            "Sea surface temperature is the highest in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where is corruption most noticeable?"),
            "Corruption is most noticeable in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where is corruption most noticeable!"),
            "Corruption is most noticeable in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where is corruption most noticeable"),
            "Corruption is most noticeable in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where were the details of the torch relay "
                        "made known?"),
            "The details of the torch relay were made known in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where is corruption most commonly noticeable?"),
            "Corruption is most commonly noticeable in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where were the soldiers under commander Yang "
                        "Wenyao trying to go?"),
            "The soldiers under commander Yang Wenyao trying "
            "to go in @placeholder ."
        )
        self.assertEqual(
            QTS.process("What a shot! Where is corruption most noticeable"),
            "What a shot! Corruption is most noticeable in @placeholder ."
        )

    def test_where_do(self):
        self.assertEqual(
            QTS.process("Where did Chopin's father get a teaching position?"),
            "Chopin 's father get a teaching position in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where did they travel after leaving Barcelona?"),
            "They travel after leaving Barcelona in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where did initial shoots for the film take place?"),
            "Initial shoots for the film take place in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where does the energy from an earthquake originate?"),
            "The energy from an earthquake originate in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where do doctors perform microorganism "
                        "identification testing?"),
            "Doctors perform microorganism identification "
            "testing in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where did initial shoots for the film take place!"),
            "Initial shoots for the film take place in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where did initial shoots for the film take place"),
            "Initial shoots for the film take place in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Where did initial shoots for the film take place???"),
            "Initial shoots for the film take place in @placeholder ."
        )
        self.assertEqual(
            QTS.process("You are very beautiful! "
                        "Where did initial shoots for the film take place?"),
            "You are very beautiful! "
            "Initial shoots for the film take place in @placeholder ."
        )
        self.assertEqual(
            QTS.process("Thank you for your free time! "
                        "It has been a pleasure for me. Where do you live? "
                        "Where did initial shoots for the film take place?"),
            "Thank you for your free time! "
            "It has been a pleasure for me. Where do you live? "
            "Initial shoots for the film take place in @placeholder ."
        )

    def test_who(self):
        self.assertEqual(
            QTS.process("Who did Chopin attend the Lower Rhenish Music "
                        "Festival with?"),
            "Chopin attend the Lower Rhenish Music Festival "
            "with @placeholder ."
        )
        self.assertEqual(
            QTS.process("Who did Güshi Khan organize a welcome ceremony for?"),
            "Güshi Khan organize a welcome ceremony for @placeholder ."
        )
        self.assertEqual(
            QTS.process("Who did Sonam Gyatso send gifts to?"),
            "Sonam Gyatso send gifts to @placeholder ."
        )
        self.assertEqual(
            QTS.process("Who is the Windows Manager?"),
            "@placeholder is the Windows Manager ."
        )
        self.assertEqual(
            QTS.process("Who was the Windows Manager in 1996?"),
            "@placeholder was the Windows Manager in 1996 ."
        )
        self.assertEqual(
            QTS.process("Who invented the pencil?"),
            "@placeholder invented the pencil ."
        )
        self.assertEqual(
            QTS.process("Who has discovered America?"),
            "@placeholder has discovered America ."
        )
        self.assertEqual(
            QTS.process("Who did Beyoncé and Parkwood Entertainment partner "
                        "with in October?"),
            "Beyoncé and Parkwood Entertainment partner with @placeholder "
            "in October ."
        )
        self.assertEqual(
            QTS.process("Who did Beyoncé perform privately for in 2011?"),
            "Beyoncé perform privately for @placeholder in 2011 ."
        )
        self.assertEqual(
            QTS.process("Who do Scout and John fight at their house?"),
            "Scout and John fight @placeholder at their house ."
        )
        self.assertEqual(
            QTS.process("Who does Beyoncé describe as the definition "
                        "of inspiration?"),
            "Beyoncé describe @placeholder as the definition of inspiration ."
        )
        self.assertEqual(
            QTS.process("Who did Beyoncé feel is an all-around entertainer?"),
            "Beyoncé feel @placeholder is an all - around entertainer ."
        )
        self.assertEqual(
            QTS.process("Who does the Chinese want to deploy to Canberra to "
                        "protect the flame?"),
            "The Chinese want @placeholder to deploy to Canberra to protect "
            "the flame ."
        )
        self.assertEqual(
            QTS.process("Who does the voice of Midna?"),
            "@placeholder does the voice of Midna ."
        )
        self.assertEqual(
            QTS.process("Who did a comparative work on a Balinese state?"),
            "@placeholder did a comparative work on a Balinese state ."
        )
        self.assertEqual(
            QTS.process("Who does the cooking at the Finch's house?"),
            "@placeholder does the cooking at the Finch 's house ."
        )
        self.assertEqual(
            QTS.process("Who did George Sand write to when admitting having "
                        "a strong affection for Frédéric?"),
            "George Sand write to @placeholder when admitting having a "
            "strong affection for Frédéric ."
        )
        self.assertEqual(
            QTS.process("Who did the Carthaginians hire to lead their army "
                        "after several losses against the Romans?"),
            "The Carthaginians hire @placeholder to lead their army "
            "after several losses against the Romans ."
        )
        self.assertEqual(
            QTS.process("Who did Beyonce perform with at the Super Bowl 50?"),
            "Beyonce perform with @placeholder at the Super Bowl 50 ."
        )
        self.assertEqual(
            QTS.process("Who did Stratford Canning convince to turn down the "
                        "treaty proposal?"),
            "Stratford Canning convince @placeholder to turn down the "
            "treaty proposal ."
        )
        self.assertEqual(
            QTS.process("Who did Paul VI feel was most important in the "
                        "Catholic Hierarchy?"),
            "Paul VI feel @placeholder was most important in the "
            "Catholic Hierarchy ."
        )

    def test_how_many(self):
        self.assertEqual(
            QTS.process("How many records combined have Beyoncé and "
                        "Jay Z sold?"),
            "@placeholder records combined Beyoncé and Jay Z have sold ."
        )
        self.assertEqual(
            QTS.process("How many certifications did RIAA give Beyoncé?"),
            "@placeholder certifications RIAA give Beyoncé ."
        )
        self.assertEqual(
            QTS.process("How many records has Beyoncé sold in the "
                        "United States?"),
            "@placeholder records Beyoncé has sold in the United States ."
        )
        self.assertEqual(
            QTS.process("How many wins does the Notre Dame men's "
                        "basketball team have?"),
            "@placeholder wins the Notre Dame men 's basketball team have ."
        )
        self.assertEqual(
            QTS.process("How many times did Chopin and Liszy perform "
                        "together in public?"),
            "@placeholder times Chopin and Liszy perform together in public ."
        )
        self.assertEqual(
            QTS.process("How many Grammy awards did Crazy in Love get?"),
            "@placeholder Grammy awards Crazy in Love get ."
        )
        self.assertEqual(
            QTS.process("How many times does the Moon rotate on its axis "
                        "during a lunar month?"),
            "@placeholder times the Moon rotate on its axis during a "
            "lunar month ."
        )
        self.assertEqual(
            QTS.process("How many basic units of information in a DNA "
                        "molecule are required to encode a single "
                        "amino acid?"),
            "@placeholder basic units of information in a DNA molecule "
            "are required to encode a single amino acid ."
        )
        self.assertEqual(
            QTS.process("How many certifications did RIAA give Beyoncé!!"),
            "@placeholder certifications RIAA give Beyoncé ."
        )
        self.assertEqual(
            QTS.process("How many certifications did RIAA give Beyoncé."),
            "@placeholder certifications RIAA give Beyoncé ."
        )

    def test_in_what(self):
        self.assertEqual(
            QTS.process("In what season in areas observing permanent daylight "
                        "saving time will it stay dark the latest "
                        "in the morning?"),
            "It will stay dark the latest in the morning in @placeholder ( "
            "season in areas observing permanent daylight saving time ) ."
        )
        self.assertEqual(
            QTS.process("In what year was the Woolworth Building completed?"),
            "The Woolworth Building was completed in @placeholder ( year ) ."
        )
        self.assertEqual(
            QTS.process("In what place did Kanye's biggest controversy "
                        "so far take place"),
            "Kanye 's biggest controversy so far take place in @placeholder "
            "( place ) ."
        )
        self.assertEqual(
            QTS.process("In what century has Dibben published two books "
                        "and other papers?"),
            "Dibben has published two books and other papers in "
            "@placeholder ( century ) ."
        )
        self.assertEqual(
            QTS.process("In what country is the riverdale neighborhood "
                        "located?"),
            "The riverdale neighborhood is located in "
            "@placeholder ( country ) ."
        )
        self.assertEqual(
            QTS.process("In what year had the library at Notre Dame reach "
                        "10,000 books?"),
            "The library at Notre Dame had reach 10,000 books in "
            "@placeholder ( year ) ."
        )
        self.assertEqual(
            QTS.process("In what two major conflicts did Portugal engage in "
                        "during the 20th century?"),
            "In @placeholder two major conflicts did Portugal engage in "
            "during the 20th century ."
        )
        self.assertEqual(
            QTS.process("In what mythology do two canines watch "
                        "over the Chinvat Bridge?"),
            "In @placeholder mythology do two canines watch over the "
            "Chinvat Bridge ."
        )
        self.assertEqual(
            QTS.process("In what section of Earth do earthquakes happen?"),
            "Earthquakes happen in @placeholder ( section of Earth ) ."
        )
        self.assertEqual(
            QTS.process("In what type of rock would a geologist most likely "
                        "find evidence of ancient life?"),
            "A geologist most likely would find evidence of ancient life "
            "in @placeholder ( type of rock ) ."
        )
        self.assertEqual(
            QTS.process("In what leaf structure is photosynthetic "
                        "tissue found?"),
            "Photosynthetic tissue is found in @placeholder "
            "( leaf structure ) ."
        )
        self.assertEqual(
            QTS.process("In what section of Earth do earthquakes happen!"),
            "Earthquakes happen in @placeholder ( section of Earth ) ."
        )
        self.assertEqual(
            QTS.process("In what section of Earth do earthquakes happen."),
            "Earthquakes happen in @placeholder ( section of Earth ) ."
        )
        self.assertEqual(
            QTS.process("In what section of Earth do earthquakes happen"),
            "Earthquakes happen in @placeholder ( section of Earth ) ."
        )
        self.assertEqual(
            QTS.process("In what section of Earth do earthquakes happen??!!"),
            "Earthquakes happen in @placeholder ( section of Earth ) ."
        )
        self.assertEqual(
            QTS.process("In what state was Camp Meade located?"),
            "Camp Meade was located in @placeholder ( state ) ."
        )
        self.assertEqual(
            QTS.process("In what year did Eisenhower propose that the pine "
                        "tree named after him be removed?"),
            "Eisenhower propose that the pine tree named after him be removed "
            "in @placeholder ( year ) ."
        )

    def test_when_do(self):
        self.assertEqual(
            QTS.process("When did American Idol showcase a new set and "
                        "stage?"),
            "American Idol showcased a new set and stage in @placeholder ."
        )
        self.assertEqual(
            QTS.process("When does American Idol showcase a new set and "
                        "stage?"),
            "American Idol showcase a new set and stage in @placeholder ."
        )
        self.assertEqual(
            QTS.process("When did the Yongle Emperor invite Deshin Shekpa "
                        "to his court?"),
            "The Yongle Emperor invited Deshin Shekpa to his court "
            "in @placeholder ."
        )
        self.assertEqual(
            QTS.process("When did she say the she is a feminist?"),
            "She said the she is a feminist in @placeholder ."
        )
        self.assertEqual(
            QTS.process("When did Beyonce leave Destiny's Child and become "
                        "a solo singer??"),
            "Beyonce leaved Destiny 's Child and become a solo singer "
            "in @placeholder ."
        )
        self.assertEqual(
            QTS.process("When did The Mamas make their debut?"),
            "The Mamas made their debut in @placeholder ."
        )
        self.assertEqual(
            QTS.process("When do contestants start singing two songs?"),
            "Contestants start singing two songs in @placeholder ."
        )
        self.assertEqual(
            QTS.process("When do intestinal microbiota develop?"),
            "Intestinal microbiota develop in @placeholder ."
        )
        self.assertEqual(
            QTS.process("When did intestinal microbiota develop?"),
            "Intestinal microbiota developed in @placeholder ."
        )
        self.assertEqual(
            QTS.process("When did the Scholastic Magazine of Notre "
                        "dame begin publishing?"),
            "The Scholastic Magazine of Notre dame begin "
            "publishing in @placeholder ."
        )
        self.assertEqual(
            QTS.process("When do the Scholastic Magazine of Notre "
                        "dame begin publishing?"),
            "The Scholastic Magazine of Notre dame begin "
            "publishing in @placeholder ."
        )
        self.assertEqual(
            QTS.process("When did Chopin last perform?"),
            "Chopin last perform in @placeholder ."
        )
        self.assertEqual(
            QTS.process("When do Chopin last perform?"),
            "Chopin last perform in @placeholder ."
        )
        self.assertEqual(
            QTS.process("When do females begin producing their sex cells "
                        "called eggs?"),
            "Females begin producing their sex cells called "
            "eggs in @placeholder ."
        )
        self.assertEqual(
            QTS.process("When does cell differentiation typically occur in "
                        "humans?"),
            "Cell differentiation typically occur in humans in @placeholder ."
        )

    def test_when_be(self):
        self.assertEqual(
            QTS.process("When was ground broke on the Eddy Street Commons "
                        "Project of Notre Dame?"),
            "Ground was broke on the Eddy Street Commons Project of "
            "Notre Dame on @placeholder ."
        )
        self.assertEqual(
            QTS.process("When were Beyonce and Jay Z married?"),
            "Beyonce and Jay Z were married on @placeholder ."
        )
        self.assertEqual(
            QTS.process("When was the soundtrack of Twilight Princess made "
                        "available?"),
            "The soundtrack of Twilight Princess was made available "
            "on @placeholder ."
        )
        self.assertEqual(
            QTS.process("When was the new Gateway Community College open?"),
            "The new Gateway Community College was open on @placeholder ."
        )
        self.assertEqual(
            QTS.process("When was Arsenal's match the first to be "
                        "televised live?"),
            "Arsenal 's match was the first to be televised live on "
            "@placeholder ."
        )
        self.assertEqual(
            QTS.process("When is Arsenal's match the first to be "
                        "televised live?"),
            "Arsenal 's match is the first to be televised live on "
            "@placeholder ."
        )
        self.assertEqual(
            QTS.process("When was ENIAC fully operational?"),
            "ENIAC was fully operational on @placeholder ."
        )
        self.assertEqual(
            QTS.process("When was my computer screen fully operational?"),
            "My computer screen fully operational was on @placeholder ."
        )
        self.assertEqual(
            QTS.process("When is ENIAC fully operational?"),
            "ENIAC is fully operational on @placeholder ."
        )
        self.assertEqual(
            QTS.process("When was the Berlin Society of Anthropology "
                        "founded by Rudolph Virchow?"),
            "The Berlin Society of Anthropology was founded by "
            "Rudolph Virchow on @placeholder ."
        )
        self.assertEqual(
            QTS.process("When was the Chrysler building built in NYC?"),
            "The Chrysler building was built in NYC on @placeholder ."
        )
        self.assertEqual(
            QTS.process("When was the term added to the dictionary?"),
            "The term was added to the dictionary on @placeholder ."
        )
        self.assertEqual(
            QTS.process("When was the fictionalized \"Chopin\" produced?"),
            "The fictionalized \" Chopin \" was produced on @placeholder ."
        )
        self.assertEqual(
            QTS.process("When is the fictionalized \"Chopin\" produced?"),
            "The fictionalized \" Chopin \" is produced on @placeholder ."
        )
        self.assertEqual(
            QTS.process("When was the mention of London removed from the "
                        "Royal Institute's name?"),
            "The mention of London was removed from the Royal Institute 's "
            "name on @placeholder ."
        )
        self.assertEqual(
            QTS.process("When was Henry Nelson Wieman invited to the "
                        "Chicago Divinity school?"),
            "Henry Nelson Wieman was invited to the Chicago Divinity "
            "school on @placeholder ."
        )
        self.assertEqual(
            QTS.process("When is Henry Nelson Wieman invited to the "
                        "Chicago Divinity school?"),
            "Henry Nelson Wieman is invited to the Chicago Divinity "
            "school on @placeholder ."
        )
        self.assertEqual(
            QTS.process("When was she on the Sports Illustrated cover?"),
            "She was on the Sports Illustrated cover on @placeholder ."
        )
        self.assertEqual(
            QTS.process("When is the beggining of the whale migration "
                        "season??"),
            "The beggining of the whale migration season is on @placeholder ."
        )
        self.assertEqual(
            QTS.process("When is the final?"),
            "The final is on @placeholder ."
        )
        self.assertEqual(
            QTS.process("When is the second-driest season in Oklahoma?"),
            "The second - driest season in Oklahoma is on @placeholder ."
        )
        self.assertEqual(
            QTS.process("When is the genitive case used?"),
            "The genitive case is used on @placeholder ."
        )

    def test_what_noun(self):
        self.assertEqual(
            QTS.process("What percentage of people were positive about "
                        "Beyonce's endorsement of Pepsi?"),
            "@placeholder ( percentage of people ) were positive about "
            "Beyonce 's endorsement of Pepsi ."
        )
        self.assertEqual(
            QTS.process("What kind of instruments are favored by Kondo?"),
            "@placeholder ( kind of instruments ) are favored by Kondo ."
        )
        self.assertEqual(
            QTS.process("What company was targeted by leaks of company "
                        "information?"),
            "@placeholder ( company ) was targeted by leaks of "
            "company information ."
        )
        self.assertEqual(
            QTS.process("What format is being covered up by the use of ipg "
                        "files?"),
            "@placeholder ( format ) being is covered up by the use of "
            "ipg files ."
        )
        self.assertEqual(
            QTS.process("What year did Chopin die?"),
            "@placeholder ( year ) Chopin died ."
        )
        self.assertEqual(
            QTS.process("What instrument did Auguste Franchomme play?"),
            "@placeholder ( instrument ) Auguste Franchomme played ."
        )
        self.assertEqual(
            QTS.process("What title did Thomas Blantz have at Notre Dame?"),
            "@placeholder ( title ) Thomas Blantz had at Notre Dame ."
        )
        self.assertEqual(
            QTS.process("What color was the metal on the U2 version "
                        "of the iPod?"),
            "@placeholder ( color ) was the metal on the U2 version of "
            "the iPod ."
        )
        self.assertEqual(
            QTS.process("What organization did Apple join to monitor "
                        "its labor policies?"),
            "@placeholder ( organization ) Apple joined to monitor its "
            "labor policies ."
        )
        self.assertEqual(
            QTS.process("What reviewer called Twilight Princess \"One of the "
                        "greatest games ever created?"),
            "@placeholder reviewer called Twilight Princess \" One of "
            "the greatest games ever created ."
        )
        self.assertEqual(
            QTS.process("What year was Chopin born?"),
            "@placeholder ( year ) Chopin was born ."
        )
        self.assertEqual(
            QTS.process("What album was released in 2016?"),
            "@placeholder ( album ) was released in 2016 ."
        )
        self.assertEqual(
            QTS.process("What year was it decided that if wolves and dogs "
                        "were one species, then their scientific name is the "
                        "name of the wild variety?"),
            "@placeholder ( year ) it was decided that if wolves and dogs "
            "were one species , then their scientific name is the "
            "name of the wild variety ."
        )
        self.assertEqual(
            QTS.process("What year was Beyoncé on the Top 20 Hot 100 "
                        "Songwriters list?"),
            "@placeholder ( year ) was Beyoncé on the Top 20 Hot 100 "
            "Songwriters list ."
        )
        self.assertEqual(
            QTS.process("What year was Chopin born???"),
            "@placeholder ( year ) Chopin was born ."
        )
        self.assertEqual(
            QTS.process("What function is an M.Div?"),
            "@placeholder ( function ) is an M.Div ."
        )
        self.assertEqual(
            QTS.process("What type was Beyonce's early music?"),
            "@placeholder ( type ) was Beyonce 's early music ."
        )
        self.assertEqual(
            QTS.process("What birth date is now considered as his actual "
                        "birthday?"),
            "@placeholder ( birth ) date is now considered as his "
            "actual birthday ."
        )
        self.assertEqual(
            QTS.process("What type of galaxy is the Milky Way?"),
            "@placeholder ( type of galaxy ) is the Milky Way ."
        )
        self.assertEqual(
            QTS.process("What type of precipitation occurs when raindrops "
                        "freeze as they fall?"),
            "@placeholder ( type of precipitation ) occurs when raindrops "
            "freeze as they fall ."
        )
        self.assertEqual(
            QTS.process("What type of cells in the eye allow humans to "
                        "perceive color?"),
            "@placeholder ( type of cells in the eye ) allow humans to "
            "perceive color ."
        )
        self.assertEqual(
            QTS.process("What type of cells in the eye did allow humans to "
                        "perceive color?"),
            "@placeholder ( type of cells in the eye ) allowed humans to "
            "perceive color ."
        )
        self.assertEqual(
            QTS.process("What type of cells in the eye do allow humans to "
                        "perceive color?"),
            "@placeholder ( type of cells in the eye ) allow humans to "
            "perceive color ."
        )
        self.assertEqual(
            QTS.process("What type of cells in the eye does allow humans to "
                        "perceive color?"),
            "@placeholder ( type of cells in the eye ) allow humans to "
            "perceive color ."
        )

    def test_which_noun(self):
        self.assertEqual(
            QTS.process("Which publication named Beyoncé the Artist of "
                        "the Decade?"),
            "@placeholder publication named Beyoncé the Artist of the Decade ."
        )
        self.assertEqual(
            QTS.process("Which event brought upon a lot of Irish immigrants "
                        "to NYC?"),
            "@placeholder event brought upon a lot of Irish immigrants "
            "to NYC ."
        )
        self.assertEqual(
            QTS.process("Which element in wood composes about 42% of "
                        "its weight?"),
            "@placeholder element in wood composes about 42 % of its weight ."
        )
        self.assertEqual(
            QTS.process("Which prize does the Architecture School at Notre "
                        "Dame give out?"),
            "@placeholder ( prize ) the Architecture School at Notre Dame "
            "give out ."
        )
        self.assertEqual(
            QTS.process("Which tunnel do 120,000 vehicles travel through a "
                        "day in NYC?"),
            "@placeholder ( tunnel ) 120,000 vehicles travel through a day "
            "in NYC ."
        )
        self.assertEqual(
            QTS.process("Which ocean does Portugal border?"),
            "@placeholder ( ocean ) Portugal border ."
        )
        self.assertEqual(
            QTS.process("Which sister did Frédéric play duets with sometimes "
                        "while being tutored at this time ?"),
            "@placeholder ( sister ) Frédéric play duets with sometimes "
            "while being tutored at this time ."
        )
        self.assertEqual(
            QTS.process("Which contestant did the band Fuel ask "
                        "to be their new lead singer?"),
            "@placeholder ( contestant ) the band Fuel asked to be "
            "their new lead singer ."
        )
        self.assertEqual(
            QTS.process("Which cathedral did Reporters Without Borders "
                        "hang another protest banner?"),
            "@placeholder ( cathedral ) Reporters Without Borders hang "
            "another protest banner ."
        )
        self.assertEqual(
            QTS.process("Which artist did Beyonce marry?"),
            "@placeholder ( artist ) Beyonce married ."
        )
        self.assertEqual(
            QTS.process("Which show did Abrams miss because he was in the "
                        "hospital?"),
            "@placeholder ( show ) Abrams missed because he was in the "
            "hospital ."
        )
        self.assertEqual(
            QTS.process("Which publication did Tucker work for?"),
            "@placeholder ( publication ) Tucker worked for ."
        )
        self.assertEqual(
            QTS.process("Which areas were shown in the Day of the Dead "
                        "scene in Spectre?"),
            "@placeholder ( areas ) were shown in the Day of the Dead "
            "scene in Spectre ."
        )
        self.assertEqual(
            QTS.process("Which year was the study published?"),
            "@placeholder ( year ) the study was published ."
        )
        self.assertEqual(
            QTS.process("Which stadium is located in east downtown "
                        "in Houston?"),
            "@placeholder ( stadium ) is located in east downtown "
            "in Houston ."
        )
        self.assertEqual(
            QTS.process("Which collection of minor poems are sometimes "
                        "attributed to Virgil?"),
            "@placeholder ( collection of minor poems ) sometimes are "
            "attributed to Virgil ."
        )
        self.assertEqual(
            QTS.process("Which contestant was surprisingly eliminated during "
                        "the top four episode?"),
            "@placeholder ( contestant ) surprisingly was eliminated during "
            "the top four episode ."
        )
        self.assertEqual(
            QTS.process("Which contestants were surprisingly eliminated "
                        "during the top four episode?"),
            "@placeholder ( contestants ) surprisingly were eliminated during "
            "the top four episode ."
        )
        self.assertEqual(
            QTS.process("Which members of British royalty were seen on the "
                        "BBC in May of 1937 ?"),
            "@placeholder ( members of British royalty ) were seen on the BBC "
            "in May of 1937 ."
        )
        self.assertEqual(
            QTS.process("Which canton is Berne the capital?"),
            "@placeholder ( canton ) is Berne the capital ."
        )
        self.assertEqual(
            QTS.process("Which direction from the island is Frightus "
                        "Rock located ?"),
            "@placeholder ( direction from the island ) is Frightus Rock "
            "located ."
        )
        self.assertEqual(
            QTS.process("Which year was the study published?"),
            "@placeholder ( year ) the study was published ."
        )
        self.assertEqual(
            QTS.process("Which judge is a country music singer ?"),
            "@placeholder ( judge ) is a country music singer ."
        )
        self.assertEqual(
            QTS.process("Which cemetery was Chopin buried in ?"),
            "@placeholder ( cemetery ) was Chopin buried in ."
        )
        self.assertEqual(
            QTS.process("Which piece is the best, in terms of "
                        "preservation condition ?"),
            "@placeholder ( piece ) is the best , in terms of preservation "
            "condition ."
        )
        self.assertEqual(
            QTS.process("Which album was darker in tone from her previous "
                        "work?"),
            "@placeholder ( album ) was darker in tone from her previous "
            "work ."
        )
        self.assertEqual(
            QTS.process("Which bridge in NYC is the busiest in the world ?"),
            "@placeholder ( bridge in NYC ) is the busiest in the world ."
        )
        self.assertEqual(
            QTS.process("Which company is responsible for the HD version "
                        "of Twilight Princess ?"),
            "@placeholder ( company ) is responsible for the HD version "
            "of Twilight Princess ."
        )
        self.assertEqual(
            QTS.process("Which court case upheld the rule of nondelegation ?"),
            "@placeholder ( court ) case upheld the rule of nondelegation ."
        )
        self.assertEqual(
            QTS.process("Which bridge in NYC is the busiest in the world ?"),
            "@placeholder ( bridge in NYC ) is the busiest in the world ."
        )
        self.assertEqual(
            QTS.process("Which film writer's work was included in leaks of "
                        "Spectre information ??"),
            "@placeholder ( film ) writer 's work was included in leaks of "
            "Spectre information ."
        )
        self.assertEqual(
            QTS.process("Which character tortures Bond ?"),
            "@placeholder ( character ) tortures Bond ."
        )
        self.assertEqual(
            QTS.process("Which generation iPod was the first to include the "
                        "30-pin dock connector?"),
            "@placeholder ( generation ) iPod was the first to include the "
            "30-pin dock connector ."
        )

    def test_which_be(self):
        self.assertEqual(
            QTS.process("Which is the smallest version of the iPod?"),
            "The smallest version of the iPod is @placeholder ."
        )
        self.assertEqual(
            QTS.process("Which was the smallest version of the iPod?"),
            "The smallest version of the iPod was @placeholder ."
        )
        self.assertEqual(
            QTS.process("Which was the first year since iPod's introduction "
                        "that no new model was released?"),
            "The first year since iPod 's introduction that no new model was "
            "released was @placeholder ."
        )
        self.assertEqual(
            QTS.process("Which is the smallest version of the iPod?"),
            "The smallest version of the iPod is @placeholder ."
        )
        self.assertEqual(
            QTS.process("Which was the most successful tour?"),
            "The most successful tour was @placeholder ."
        )
        self.assertEqual(
            QTS.process("Which are the most beautiful flowers?"),
            "The most beautiful flowers are @placeholder ."
        )
        self.assertEqual(
            QTS.process("Which was the most important battle fought "
                        "in Chihuahua?"),
            "The most important battle fought in Chihuahua was @placeholder ."
        )
        self.assertEqual(
            QTS.process("Which is more efficient: compact fluorescent or "
                        "LED lights?"),
            "More efficient : compact fluorescent or LED lights is "
            "@placeholder ."
        )

    def test_in_which_noun(self):
        self.assertEqual(
            QTS.process("In which location do students of the School of "
                        "Architecture of Notre Dame spend their 3rd year?"),
            "Students of the School of Architecture of Notre Dame spend "
            "their 3rd year in @placeholder ( location ) ."
        )
        self.assertEqual(
            QTS.process("In which region does Portugal have vast reserves "
                        "of iron and coal?"),
            "Portugal have vast reserves of iron and coal in "
            "@placeholder ( region ) ."
        )
        self.assertEqual(
            QTS.process("In which type of organism do the smallest genomes "
                        "occur?"),
            "The smallest genomes occur in @placeholder ( type of organism ) ."
        )
        self.assertEqual(
            QTS.process("In which hemisphere does bird migration primarily "
                        "happen?"),
            "Bird migration primarily happen in @placeholder ( hemisphere ) ."
        )
        self.assertEqual(
            QTS.process("In which century did Portugal see the arrival of "
                        "Modernism?"),
            "Portugal saw the arrival of Modernism in @placeholder "
            "( century ) ."
        )
        self.assertEqual(
            QTS.process("In which decade did Beyonce become famous?"),
            "Beyonce became famous in @placeholder ( decade ) ."
        )
        self.assertEqual(
            QTS.process("In which year did Alfonso III likely die?"),
            "Alfonso III likely died in @placeholder ( year ) ."
        )
        self.assertEqual(
            QTS.process("In which village did Frédéric first experience "
                        "rural Polish folk music?"),
            "Frédéric first experience rural Polish folk music in "
            "@placeholder ( village ) ."
        )
        self.assertEqual(
            QTS.process("In which region of Portugal did the Muslim "
                        "population stay?"),
            "The Muslim population stayed in @placeholder ( region of "
            "Portugal ) ."
        )
        self.assertEqual(
            QTS.process("In which season was online voting introduced?"),
            "Online voting was introduced in @placeholder ( season ) ."
        )
        self.assertEqual(
            QTS.process("In which branch of Buddhism is it believed that "
                        "there can be no divine salvation or forgiveness "
                        "for karma?"),
            "It is believed that there can be no divine salvation or "
            "forgiveness for karma in @placeholder ( branch of Buddhism ) ."
        )
        self.assertEqual(
            QTS.process("In which city was the stamp officially released?"),
            "The stamp officially was released in @placeholder ( city ) ."
        )
        self.assertEqual(
            QTS.process("In which year was reports about Beyonce performing "
                        "for Muammar Gaddafi surface?"),
            "Reports about Beyonce performing for Muammar Gaddafi surface "
            "was in @placeholder ( year ) ."
        )
        self.assertEqual(
            QTS.process("In which direction is Puerto Rico from the island "
                        "of Saint-Barthélemy?"),
            "Puerto Rico from the island of Saint - Barthélemy is in "
            "@placeholder ( direction ) ."
        )
        self.assertEqual(
            QTS.process("In which music video did Beyoncé star as Jay Z's "
                        "girlfriend, creating speculation about their "
                        "relationship?"),
            "Beyoncé starred as Jay Z 's girlfriend , creating speculation "
            "about their relationship in @placeholder ( music video ) ."
        )
        self.assertEqual(
            QTS.process("In which war-era country was the Holocaust "
                        "immortalized?"),
            "The Holocaust was immortalized in @placeholder ( war - era "
            "country ) ."
        )
        self.assertEqual(
            QTS.process("In which book, was the term \"computer\" "
                        "first used?"),
            "The term \" computer \" first used was in @placeholder ( book ) ."
        )
        self.assertEqual(
            QTS.process("In which era, did the first phylum of multicellular "
                        "organisms appear?"),
            "The first phylum of multicellular organisms appeared in "
            "@placeholder ( era ) ."
        )
        self.assertEqual(
            QTS.process("In which Bond story did the name Oberhauser first "
                        "appear?"),
            "The name Oberhauser first appeared in @placeholder "
            "( Bond story ) ."
        )
        self.assertEqual(
            QTS.process("In which round of UEFA Euro 2012 was England "
                        "eliminated?!?"),
            "England was eliminated in @placeholder ( round of UEFA Euro 2012 "
            ") ."
        )

    def test_why(self):
        self.assertEqual(
            QTS.process("Why does genocide often go unpunished?"),
            "Genocide often go unpunished because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why do people eat Gaejang-guk in the summer months?"),
            "People eat Gaejang - guk in the summer months "
            "because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why did John Locke believe that one person cannot "
                        "enslave another?"),
            "John Locke believed that one person can not enslave "
            "another because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why did the NFL Network begin to broadcast "
                        "games again?"),
            "The NFL Network began to broadcast games again "
            "because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why was Nasser rejected from the Academy?"),
            "Nasser was rejected from the Academy because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why is Nasser rejected from the Academy?"),
            "Nasser is rejected from the Academy because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why are divers attracted to Bermuda?"),
            "Divers are attracted to Bermuda because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why is Chan suing the Hong Kong government?"),
            "Chan is suing the Hong Kong government because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why was he indentured for life?"),
            "He was indentured for life because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why was the Royal College of Chemistry founded?"),
            "The Royal College of Chemistry was founded because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why do you think she is beautiful?"),
            "You think she is beautiful because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why is she nice?"),
            "She is nice because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why did the train catch fire?"),
            "The train catch fire because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why did interest in solar water heating decrease "
                        "in the 1980s?"),
            "Interest in solar water heating decrease in the 1980s "
            "because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why was the first route not taken?"),
            "The first route not was taken because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why were flights delayed and diverted?"),
            "Flights were delayed and diverted because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why are long sentences in a modern preamble "
                        "formatted into multiple paragraphs?"),
            "Long sentences in a modern preamble are formatted into multiple "
            "paragraphs because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why is the use of solar balloons typically limited "
                        "to the toy market?"),
            "The use of solar balloons typically is limited to the toy market "
            "because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why was Crystal Bowersox in the hospital during the "
                        "week of the top 20 on American Idol ??"),
            "Crystal Bowersox was in the hospital during the week of the top "
            "20 on American Idol because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why is Lisbon a popular stopover for many "
                        "foreign airlines?"),
            "Lisbon is a popular stopover for many foreign airlines "
            "because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why were French troops in Bern?"),
            "French troops were in Bern because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why is there difficulty in defining process "
                        "theology?"),
            "There is difficulty in defining process theology "
            "because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why was there concerns in 2010?"),
            "There was concerns in 2010 because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why type of conflict is sociocultural anthropology "
                        "interested in?"),
            "Type of conflict is sociocultural anthropology interested "
            "in because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why was the Yongle Emperor said to have been "
                        "planning to send military forces into Tibet?"),
            "The Yongle Emperor was said to have been planning to send "
            "military forces into Tibet because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why are somatic cells in organisms considered "
                        "diploid cells?"),
            "Somatic cells in organisms are considered diploid cells because "
            "@placeholder ."
        )
        self.assertEqual(
            QTS.process("Why is protein an important part of a healthy diet?"),
            "Protein is an important part of a healthy diet "
            "because @placeholder ."
        )
        self.assertEqual(
            QTS.process("Why is natural selection said to act on the "
                        "phenotype of an organism, rather than the genotype?"),
            "Natural selection is said to act on the phenotype of an organism "
            ", rather than the genotype because @placeholder ."
        )

    def test_what_verb(self):
        self.assertEqual(
            QTS.process("What can happen when antibiotics are used with "
                        "other drugs?"),
            "@placeholder can happen when antibiotics are used with other "
            "drugs ."
        )
        self.assertEqual(
            QTS.process("What could happen when antibiotics are used with "
                        "other drugs?"),
            "@placeholder could happen when antibiotics are used with other "
            "drugs ."
        )
        self.assertEqual(
            QTS.process("What cannot happen when antibiotics are used with "
                        "other drugs?"),
            "@placeholder can not happen when antibiotics are used with other "
            "drugs ."
        )
        self.assertEqual(
            QTS.process("What couldn't happen when antibiotics are used with "
                        "other drugs?"),
            "@placeholder could not happen when antibiotics are used with "
            "other drugs ."
        )
        self.assertEqual(
            QTS.process("What can be used to shoot without the need to "
                        "manually target enemies?"),
            "@placeholder can be used to shoot without the need to manually "
            "target enemies ."
        )
        self.assertEqual(
            QTS.process("What can happen if people are exposed to antibiotics "
                        "at a young age?"),
            "@placeholder can happen if people are exposed to antibiotics at "
            "a young age ."
        )
        self.assertEqual(
            QTS.process("What should be used to answer ultimate questions on "
                        "morality and meaning?"),
            "@placeholder should be used to answer ultimate questions on "
            "morality and meaning ."
        )
        self.assertEqual(
            QTS.process("What shouldn't be used to answer ultimate questions "
                        "on morality and meaning?"),
            "@placeholder should not be used to answer ultimate questions on "
            "morality and meaning ."
        )
        self.assertEqual(
            QTS.process("What may be used to answer ultimate questions on "
                        "morality and meaning?"),
            "@placeholder may be used to answer ultimate questions on "
            "morality and meaning ."
        )
        self.assertEqual(
            QTS.process("What might be used to answer ultimate questions on "
                        "morality and meaning?"),
            "@placeholder might be used to answer ultimate questions on "
            "morality and meaning ."
        )
        self.assertEqual(
            QTS.process("What may not be used to answer ultimate questions on "
                        "morality and meaning?"),
            "@placeholder may not be used to answer ultimate questions on "
            "morality and meaning ."
        )
        self.assertEqual(
            QTS.process("What should be done with a glass cover slip after "
                        "it has been used?"),
            "@placeholder should be done with a glass cover slip after it "
            "has been used ."
        )
        self.assertEqual(
            QTS.process("What may form as a direct result of a star "
                        "collapsing?"),
            "@placeholder may form as a direct result of a star collapsing ."
        )
        self.assertEqual(
            QTS.process("What can illegal children be registered as in place "
                        "of their dead siblings?"),
            "Illegal children can be registered as @placeholder in place of "
            "their dead siblings ."
        )
        self.assertEqual(
            QTS.process("What could we monitor electronically that could "
                        "help inform new methods of wood protection?"),
            "We could monitor electronically @placeholder that could "
            "help inform new methods of wood protection ."
        )
        self.assertEqual(
            QTS.process("What can Plainsong or Gregorian chant also "
                        "be called??"),
            "Plainsong or Gregorian chant can also be called @placeholder ."
        )
        self.assertEqual(
            QTS.process("What can small mutations be caused by?"),
            "Small mutations can be caused by @placeholder ."
        )
        self.assertEqual(
            QTS.process("What may small mutations be caused by?"),
            "Small mutations may be caused by @placeholder ."
        )
        self.assertEqual(
            QTS.process("What should architecture be assumed to "
                        "promote, according to Rondanini?"),
            "Architecture should be assumed @placeholder to promote , "
            "according to Rondanini ."
        )
        self.assertEqual(
            QTS.process("What can the scent of vanilla be used for?"),
            "The scent of vanilla can be used for @placeholder ."
        )
        self.assertEqual(
            QTS.process("What should the cost of incentives for producing "
                        "solar energy be considered?"),
            "The cost of incentives for producing solar energy should be "
            "considered @placeholder ."
        )
        self.assertEqual(
            QTS.process("What should the government of China be responsible "
                        "for providing to earthquake survivors?"),
            "The government of China should be responsible for providing "
            "@placeholder to earthquake survivors ."
        )
        self.assertEqual(
            QTS.process("What could you call someone who lives "
                        "in Southampton?"),
            "You could call @placeholder someone who lives in Southampton ."
        )
        self.assertEqual(
            QTS.process("What can each forwarding operation location "
                        "provide?"),
            "Each forwarding operation location can provide @placeholder ."
        )
        self.assertEqual(
            QTS.process("What can the displacement of ice cause?"),
            "The displacement of ice can cause @placeholder ."
        )
        self.assertEqual(
            QTS.process("What would have been the top benefit for "
                        "dogs in camps?"),
            "@placeholder would have been the top benefit for dogs in camps ."
        )
        self.assertEqual(
            QTS.process("What wouldn't have been the top benefit for "
                        "dogs in camps?"),
            "@placeholder would not have been the top benefit for dogs "
            "in camps ."
        )
        self.assertEqual(
            QTS.process("What will have been the top benefit for "
                        "dogs in camps?"),
            "@placeholder will have been the top benefit for dogs in camps ."
        )
        self.assertEqual(
            QTS.process("What will orchestras use to augment their "
                        "regular rosters?"),
            "Orchestras will use @placeholder to augment their regular "
            "rosters ."
        )
        self.assertEqual(
            QTS.process("What will happen if too many consumers save or "
                        "pay down debt simultaneously?"),
            "@placeholder will happen if too many consumers save or pay "
            "down debt simultaneously ."
        )
        self.assertEqual(
            QTS.process("What would have led to the starvation of 80 million "
                        "people in the Soviet Union?"),
            "@placeholder would have led to the starvation of 80 million "
            "people in the Soviet Union ."
        )
        self.assertEqual(
            QTS.process("What has the ASA identified as being "
                        "ethically dangerous?"),
            "The ASA has identified as @placeholder being ethically "
            "dangerous ."
        )
        self.assertEqual(
            QTS.process("What has been falsely credited to Chopin?"),
            "@placeholder has been falsely credited to Chopin ."
        )
        self.assertEqual(
            QTS.process("What have governments done to offset the reduction "
                        "in private sector demand?"),
            "Governments have done @placeholder to offset the reduction in "
            "private sector demand ."
        )
        self.assertEqual(
            QTS.process("What had governments done to offset the reduction "
                        "in private sector demand?"),
            "Governments had done @placeholder to offset the reduction in "
            "private sector demand ."
        )
        self.assertEqual(
            QTS.process("What have some people argued correlates with time "
                        "shifts from daylight savings?"),
            "Some people have argued @placeholder correlates with time shifts "
            "from daylight savings ."
        )
        self.assertEqual(
            QTS.process("What has sociocultural anthropology been heavily "
                        "influenced by?"),
            "Sociocultural anthropology has been heavily influenced "
            "by @placeholder ."
        )
        self.assertEqual(
            QTS.process("What had to be evacuated due to potential flooding?"),
            "@placeholder had to be evacuated due to potential flooding ."
        )
        self.assertEqual(
            QTS.process("What has happened to photovoltaic in the past "
                        "20 years??"),
            "@placeholder has happened to photovoltaic in the past 20 years ."
        )
        self.assertEqual(
            QTS.process("What causes diarrhea?"),
            "@placeholder causes diarrhea ."
        )
        self.assertEqual(
            QTS.process("What sits on top of the Main Building at "
                        "Notre Dame?!??"),
            "@placeholder sits on top of the Main Building at Notre Dame ."
        )
        self.assertEqual(
            QTS.process("What had to be evacuated due to potential flooding?"),
            "@placeholder had to be evacuated due to potential flooding ."
        )
        self.assertEqual(
            QTS.process("What happened to the cargo train?"),
            "@placeholder happened to the cargo train ."
        )
        self.assertEqual(
            QTS.process("What happened to the cargo train."),
            "@placeholder happened to the cargo train ."
        )
        self.assertEqual(
            QTS.process("What happened to the cargo train"),
            "@placeholder happened to the cargo train ."
        )

    def test_what_general(self):
        self.assertEqual(
            QTS.process("What Beyoncé song was song of the year on 2010?"),
            "Song of the year on 2010 was @placeholder ( Beyoncé song ) ."
        )
        self.assertEqual(
            QTS.process("What 1945 film was a fictionalized accounting of "
                        "the relationship between Chopin and Sand?"),
            "A fictionalized accounting of the relationship between Chopin "
            "and Sand was @placeholder ( 1945 film ) ."
        )
        self.assertEqual(
            QTS.process("What natural disasters were occurring in "
                        "Wenchuan County?"),
            "Occurring in Wenchuan County were "
            "@placeholder ( natural disasters ) ."
        )
        self.assertEqual(
            QTS.process("What mental health issue did Beyonce go through?"),
            "Beyonce go through @placeholder ( mental health issue ) ."
        )
        self.assertEqual(
            QTS.process("What other practices do Buddhists adhere to?"),
            "Buddhists adhere to @placeholder ( other practices ) ."
        )
        self.assertEqual(
            QTS.process("What other mission besides dropout and illiteracy "
                        "rates did the Kanye West Foundation seek "
                        "to improve?"),
            "The Kanye West Foundation seek to improve @placeholder ( other "
            "mission besides dropout and illiteracy rates ) ."
        )
        self.assertEqual(
            QTS.process("What 2005 publication in its third edition kept to "
                        "that ruling?"),
            "@placeholder ( 2005 publication in its third edition ) kept "
            "to that ruling ."
        )
        self.assertEqual(
            QTS.process("What mountain range runs through Tajikistan?"),
            "@placeholder ( mountain ) range runs through Tajikistan ."
        )
        self.assertEqual(
            QTS.process("What annual sporting competition features the "
                        "Wanamaker Mile?"),
            "@placeholder ( annual sporting competition ) features the "
            "Wanamaker Mile ."
        )
        self.assertEqual(
            QTS.process("What famous soccer player played for the New "
                        "York Cosmos?"),
            "@placeholder ( famous soccer player ) played for the New York "
            "Cosmos ."
        )
        self.assertEqual(
            QTS.process("What three reasons has sociocultural anthropology "
                        "been heavily influenced by?"),
            "Sociocultural anthropology has been heavily influenced "
            "by @placeholder ( three reasons ) ."
        )
        self.assertEqual(
            QTS.process("What big cats in Indonesia also attack dogs?"),
            "@placeholder ( big cats in Indonesia ) also attack dogs ."
        )
        self.assertEqual(
            QTS.process("What younger sister of Maria also appeared "
                        "in Destiny's Child?"),
            "@placeholder ( younger sister of Maria ) also appeared in "
            "Destiny 's Child ."
        )
        self.assertEqual(
            QTS.process("What modern brewers often first began as beer "
                        "houses?"),
            "@placeholder ( modern brewers ) often first began as beer "
            "houses ."
        )
        self.assertEqual(
            QTS.process("What musical concept did Chopin exploit?"),
            "Chopin exploit @placeholder ( musical concept ) ."
        )
        self.assertEqual(
            QTS.process("What Robert Redford movie was shot here in 1942?"),
            "Shot here in 1942 was @placeholder ( Robert Redford movie ) ."
        )
        self.assertEqual(
            QTS.process("What musical comedy did Beyoncé star in along with "
                        "Cuba Gooding, Jr. in 2003?"),
            "Beyoncé star in along with Cuba Gooding , Jr. in 2003 "
            "@placeholder ( musical comedy ) ."
        )
        self.assertEqual(
            QTS.process("What French Magazine cover did the media criticize?"),
            "The media criticize @placeholder ( French Magazine cover ) ."
        )
        self.assertEqual(
            QTS.process("What about Beyonce has influenced many "
                        "entertainers?"),
            "@placeholder ( about Beyonce ) has influenced many entertainers ."
        )
        self.assertEqual(
            QTS.process("What besides investment is responsible for the high "
                        "standard of living on the island?"),
            "Responsible for the high standard of living on the island is "
            "@placeholder ( besides investment ) ."
        )
        self.assertEqual(
            QTS.process("What 2 critics gave Twilight Princess awards for "
                        "Best Graphics and Best Story????"),
            "@placeholder ( 2 critics ) gave Twilight Princess awards for "
            "Best Graphics and Best Story ."
        )
        self.assertEqual(
            QTS.process("What new genre di John Field invent?"),
            "@placeholder new genre di John Field invent ."
        )

    def test_how_much(self):
        self.assertEqual(
            QTS.process("How much did Schwarzenegger make from the film "
                        "Total Recall, on top of 15% of gross?"),
            "@placeholder Schwarzenegger made from the film Total Recall , "
            "on top of 15 % of gross ."
        )
        self.assertEqual(
            QTS.process("How much did she earn in 2014?"),
            "@placeholder she earned in 2014 ."
        )
        self.assertEqual(
            QTS.process("How much more money does the city give to the state "
                        "of New York annually than it receives?"),
            "@placeholder more money the city give to the state of New York "
            "annually than it receives ."
        )
        self.assertEqual(
            QTS.process("How much does the Olympic Torch weigh?"),
            "@placeholder the Olympic Torch weigh ."
        )
        self.assertEqual(
            QTS.process("How much tax revenue does the securities "
                        "industry generate?"),
            "@placeholder tax revenue the securities industry generate ."
        )
        self.assertEqual(
            QTS.process("How much had Spectre made in its first month "
                        "in China?"),
            "@placeholder Spectre had made in its first month in China ."
        )
        self.assertEqual(
            QTS.process("How much has the Amity Foundation designated for "
                        "disaster relief?"),
            "@placeholder the Amity Foundation has designated for disaster "
            "relief ."
        )
        self.assertEqual(
            QTS.process("How much did JPMorgan estimate was the average "
                        "recovery rate for high quality CDOs that had been "
                        "liquidated?"),
            "@placeholder JPMorgan estimated was the average recovery rate "
            "for high quality CDOs that had been liquidated ."
        )
        self.assertEqual(
            QTS.process("How much money had been donated by May 14?"),
            "@placeholder money had been donated by May 14 ."
        )
        self.assertEqual(
            QTS.process("How much is being spent on a water purification "
                        "plant at the Croton Watershed?"),
            "@placeholder is being spent on a water purification plant at "
            "the Croton Watershed ."
        )
        self.assertEqual(
            QTS.process("How much was China going to invest in the European "
                        "Galileo positioning system project?"),
            "@placeholder was China going to invest in the European Galileo "
            "positioning system project ."
        )
        self.assertEqual(
            QTS.process("How much did hunters spend in 2001??"),
            "@placeholder hunters spent in 2001 ."
        )
        self.assertEqual(
            QTS.process("How much have hunters spent in 2001?!"),
            "@placeholder hunters have spent in 2001 ."
        )
        self.assertEqual(
            QTS.process("How much of Greece's economy is comprised of "
                        "industrial sectors?"),
            "@placeholder of Greece 's economy is comprised of industrial "
            "sectors ."
        )
        self.assertEqual(
            QTS.process("How much had average U.S. housing prices declined "
                        "by September 2008?"),
            "@placeholder average U.S. housing prices had declined by "
            "September 2008 ."
        )

    def test_how_long(self):
        self.assertEqual(
            QTS.process("How long did the plan last?"),
            "@placeholder ( long ) the plan lasted ."
        )
        self.assertEqual(
            QTS.process("How long before the quake did Cyclone Nargis "
                        "strike Burma?"),
            "@placeholder ( long ) before the quake Cyclone Nargis "
            "struck Burma ."
        )
        self.assertEqual(
            QTS.process("How long does the identification process take?"),
            "@placeholder ( long ) the identification process take ."
        )
        self.assertEqual(
            QTS.process("How long has the single congressional district "
                        "been Republican?"),
            "@placeholder ( long ) the single congressional district has been "
            "Republican ."
        )
        self.assertEqual(
            QTS.process("How long had it been since an earthquake of similar "
                        "magnitude?"),
            "@placeholder ( long ) it had been since an earthquake of similar "
            "magnitude ."
        )
        self.assertEqual(
            QTS.process("How long has the domestic dog been selectively "
                        "bred?"),
            "@placeholder ( long ) the domestic dog has been selectively "
            "bred ."
        )
        self.assertEqual(
            QTS.process("How long has this cultural diffusion been "
                        "happening?"),
            "@placeholder ( long ) this cultural diffusion has been "
            "happening ."
        )
        self.assertEqual(
            QTS.process("How long had this cultural diffusion been "
                        "happening?"),
            "@placeholder ( long ) this cultural diffusion had been "
            "happening ."
        )
        self.assertEqual(
            QTS.process("How long has the system of staff notation been "
                        "in use?"),
            "@placeholder ( long ) the system of staff notation has been in "
            "use ."
        )
        self.assertEqual(
            QTS.process("How long did it actually take Whitehead and Russell "
                        "to complete Principia Mathematica?"),
            "@placeholder ( long ) it actually took Whitehead and Russell to "
            "complete Principia Mathematica ."
        )
        self.assertEqual(
            QTS.process("How long has Miami been the world's top cruise "
                        "passenger port?"),
            "@placeholder ( long ) Miami has been the world 's top cruise "
            "passenger port ."
        )

    def test_how_do(self):
        self.assertEqual(
            QTS.process("How do dogs mark their territory?"),
            "Dogs mark their territory by @placeholder ."
        )
        self.assertEqual(
            QTS.process("How does flagellum function within the cell?"),
            "Flagellum function within the cell by @placeholder ."
        )
        self.assertEqual(
            QTS.process("How does the lifecycle of most insects typically "
                        "begin?"),
            "The lifecycle of most insects typically begin by @placeholder ."
        )
        self.assertEqual(
            QTS.process("How did Waitz define anthropology?"),
            "Waitz defined anthropology as @placeholder ."
        )
        self.assertEqual(
            QTS.process("How did Etta James influence her?"),
            "Etta James influenced her by @placeholder ."
        )
        self.assertEqual(
            QTS.process("How did Beyonce deal with the miscarriage of "
                        "her child?"),
            "Beyonce dealt with the miscarriage of her child by @placeholder ."
        )
        self.assertEqual(
            QTS.process("How did Yuji Yagi say the quake happened?"),
            "Yuji Yagi said the quake happened by @placeholder ."
        )
        self.assertEqual(
            QTS.process("How did the Encyclopedia Americana describe the "
                        "Yuan Dynasty?"),
            "The Encyclopedia Americana described the Yuan Dynasty as "
            "@placeholder ."
        )
        self.assertEqual(
            QTS.process("How does he describe the Yuan Dynasty?"),
            "He describe the Yuan Dynasty as @placeholder ."
        )
        self.assertEqual(
            QTS.process("How did Descartes' distinguish types of existence?"),
            "Descartes ' distinguish types of existence by @placeholder ."
        )
        self.assertEqual(
            QTS.process("How did the actual sales of the G4's compare to the "
                        "sales expectations?"),
            "The actual sales of the G4 's compare to the sales expectations "
            "by @placeholder ."
        )
        self.assertEqual(
            QTS.process("How did Top 40 radio what ifmusic change during "
                        "this era?"),
            "Top 40 radio what ifmusic change during this era by "
            "@placeholder ."
        )
        self.assertEqual(
            QTS.process("How does it effect elections ?"),
            "It effect elections by @placeholder ."
        )
        self.assertEqual(
            QTS.process("How did Creole English come about?"),
            "Creole English came about by @placeholder ."
        )
        self.assertEqual(
            QTS.process("How did the Mimamsa school view the soul?"),
            "The Mimamsa school viewed the soul as @placeholder ."
        )
        self.assertEqual(
            QTS.process("How did post-punk take on rock and roll?"),
            "Post - punk took on rock and roll by @placeholder ."
        )

    def test_how_be(self):
        self.assertEqual(
            QTS.process("How was Blue Ivy credited on Glory?"),
            "Blue Ivy was credited on Glory as @placeholder ."
        )
        self.assertEqual(
            QTS.process("How is each object related to other things?"),
            "Each object is related to other things by @placeholder ."
        )
        self.assertEqual(
            QTS.process("How is Nanjing seen, from a cultural perspective?"),
            "Nanjing is seen , from a cultural perspective as @placeholder ."
        )
        self.assertEqual(
            QTS.process("How were comics published when serialization became "
                        "less common?"),
            "Comics were published when serialization became less common by "
            "@placeholder ."
        )
        self.assertEqual(
            QTS.process("How is Valencian classified?"),
            "Valencian is classified as @placeholder ."
        )
        self.assertEqual(
            QTS.process("How were earthquakes simulated on the architectural "
                        "models?"),
            "Earthquakes were simulated on the architectural models by "
            "@placeholder ."
        )
        self.assertEqual(
            QTS.process("How are the slufonamides,quinolones, and "
                        "oxazolidinones created?"),
            "The slufonamides , quinolones , and oxazolidinones are created "
            "by @placeholder ."
        )
        self.assertEqual(
            QTS.process("How is thermal mass used to keep buildings cool?"),
            "Thermal mass is used to keep buildings cool by @placeholder ."
        )
        self.assertEqual(
            QTS.process("How was thermal mass used to keep buildings cool?"),
            "Thermal mass was used to keep buildings cool by @placeholder ."
        )
        self.assertEqual(
            QTS.process("How is H2 used in electrical generators at "
                        "power stations?"),
            "H2 is used in electrical generators at power stations "
            "by @placeholder ."
        )
        self.assertEqual(
            QTS.process("How were these stores different than most during "
                        "that time?"),
            "These stores were different than most during that time by "
            "@placeholder ."
        )
        self.assertEqual(
            QTS.process("How are predators beneficial to agriculture???"),
            "Predators are beneficial to agriculture by @placeholder ."
        )
        self.assertEqual(
            QTS.process("How were predators beneficial to agriculture?!"),
            "Predators were beneficial to agriculture by @placeholder ."
        )
        self.assertEqual(
            QTS.process("How was the setting for the Image versions of "
                        "Marvel characters different from the "
                        "official comics?"),
            "The setting for the Image versions of Marvel characters was "
            "different from the official comics by @placeholder ."
        )
        self.assertEqual(
            QTS.process("How is the retail market of Mexico City?"),
            "The retail market of Mexico City is @placeholder ."
        )
        self.assertEqual(
            QTS.process("How is Catalan different from other Romance "
                        "languages?"),
            "Catalan is different from other Romance languages by "
            "@placeholder ."
        )
        self.assertEqual(
            QTS.process("How are vowel alternances in Catalan?"),
            "Vowel alternances in Catalan are @placeholder ."
        )
        self.assertEqual(
            QTS.process("How is a digimon reborn?"),
            "A digimon reborn is @placeholder ."
        )
        self.assertEqual(
            QTS.process("How is the Cambrian Explosion best described?"),
            "The Cambrian Explosion best is described as @placeholder ."
        )
        self.assertEqual(
            QTS.process("How is the stratosphere different from the "
                        "troposphere?"),
            "The stratosphere is different from the troposphere "
            "by @placeholder ."
        )

    def test_the(self):
        self.assertEqual(
            QTS.process("The French words Notre Dame du Lac translate to "
                        "what in English?"),
            "The French words Notre Dame du Lac translate to @placeholder "
            "in English ."
        )
        self.assertEqual(
            QTS.process("The amount of professors at Notre Dame increased by "
                        "what amount under Malloy?"),
            "The amount of professors at Notre Dame increased by @placeholder "
            "amount under Malloy ."
        )
        self.assertEqual(
            QTS.process("The Nidnakath of the Jataka tales of the Theravada "
                        "is attributed to who?"),
            "The Nidnakath of the Jataka tales of the Theravada is attributed "
            "to @placeholder ."
        )
        self.assertEqual(
            QTS.process("The presence of the Altan Khan in the west reduced "
                        "whos influence?"),
            "The presence of the Altan Khan in the west reduced "
            "@placeholder s influence ."
        )
        self.assertEqual(
            QTS.process("The British government detained who in Saint "
                        "Helena?"),
            "The British government detained @placeholder in Saint Helena ."
        )
        self.assertEqual(
            QTS.process("The highest peak of the Western Alps is where?"),
            "The highest peak of the Western Alps is @placeholder ."
        )
        self.assertEqual(
            QTS.process("The main ports for London were relocated to where?"),
            "The main ports for London were relocated to @placeholder ."
        )
        self.assertEqual(
            QTS.process("The Sephardic Jewish community in London is "
                        "affiliated with which Synagogue?"),
            "The Sephardic Jewish community in London is affiliated with "
            "@placeholder Synagogue ."
        )
        self.assertEqual(
            QTS.process("The origin of which community can be traced to the "
                        "16th century?"),
            "The origin of @placeholder community can be traced to the "
            "16th century ."
        )
        self.assertEqual(
            QTS.process("The recent Indiana Jones movie featured how many of "
                        "the local citizen in film?"),
            "The recent Indiana Jones movie featured @placeholder of the "
            "local citizen in film ."
        )
        self.assertEqual(
            QTS.process("The delay in support by certain powerful members "
                        "meant the Convention was largely powerless for over "
                        "how many decades?"),
            "The delay in support by certain powerful members meant the "
            "Convention was largely powerless for over @placeholder decades ."
        )
        self.assertEqual(
            QTS.process("The Census Bureau had gone from two categories to "
                        "how many by the 1990s?"),
            "The Census Bureau had gone from two categories to @placeholder "
            "by the 1990s ."
        )
        self.assertEqual(
            QTS.process("The Greek Monarchy was abolished when?"),
            "The Greek Monarchy was abolished @placeholder ."
        )
        self.assertEqual(
            QTS.process("The Mamas first appearance was when?"),
            "The Mamas first appearance was @placeholder ."
        )
        self.assertEqual(
            QTS.process("The world's best selling celebrity perfume line "
                        "belongs to whom?"),
            "The world 's best selling celebrity perfume line belongs to "
            "@placeholder ."
        )
        self.assertEqual(
            QTS.process("The parent company of Tidal became under the "
                        "ownership of whom in 2015?"),
            "The parent company of Tidal became under the ownership of "
            "@placeholder in 2015 ."
        )
        self.assertEqual(
            QTS.process("The Duchy of Warsaw was created by whom?"),
            "The Duchy of Warsaw was created by @placeholder ."
        )
        self.assertEqual(
            QTS.process("The second truth is?"),
            "The second truth is @placeholder ."
        )
        self.assertEqual(
            QTS.process("the vinaya was recited by?"),
            "the vinaya was recited by @placeholder ."
        )
        self.assertEqual(
            QTS.process("The only prior season to have matching controversy "
                        "over the winner was?"),
            "The only prior season to have matching controversy over the "
            "winner was @placeholder ."
        )
        self.assertEqual(
            QTS.process("The second truth is"),
            "The second truth is @placeholder ."
        )
        self.assertEqual(
            QTS.process("The second truth is."),
            "The second truth is @placeholder ."
        )
        self.assertEqual(
            QTS.process("The second truth is ..."),
            "The second truth is @placeholder ."
        )
        self.assertEqual(
            QTS.process("The score determines how various parts are "
                        "coordinated, pitch, and what other detail?"),
            "The score determines how various parts are coordinated , "
            "pitch , and @placeholder other detail ."
        )
        self.assertEqual(
            QTS.process("The majority of contemporary Slavic populations who "
                        "profess a religion are what?"),
            "The majority of contemporary Slavic populations who profess a "
            "religion are @placeholder ."
        )
        self.assertEqual(
            QTS.process("The state produces lots of dairy which large "
                        "processors of what dairy product?"),
            "The state produces lots of dairy which large processors of "
            "@placeholder dairy product ."
        )
        self.assertEqual(
            QTS.process("The interior of Earth is made up of several "
                        "physically different layers. The solid layer of "
                        "Earth that moves over a viscous layer is "
                        "called the?"),
            "The interior of Earth is made up of several physically different "
            "layers. The solid layer of Earth that moves over a viscous layer "
            "is called the @placeholder ."
        )
        self.assertEqual(
            QTS.process("The interior of Earth is made up of several "
                        "physically different layers. The solid layer of "
                        "Earth that moves over a viscous layer is "
                        "called the"),
            "The interior of Earth is made up of several physically different "
            "layers. The solid layer of Earth that moves over a viscous layer "
            "is called the @placeholder ."
        )
        self.assertEqual(
            QTS.process("The interior of Earth is made up of several "
                        "physically different layers. The solid layer of "
                        "Earth that moves over a viscous layer is "
                        "called the ..."),
            "The interior of Earth is made up of several physically different "
            "layers. The solid layer of Earth that moves over a viscous layer "
            "is called the @placeholder ."
        )
        self.assertEqual(
            QTS.process("The correct procedure after completing a laboratory "
                        "experiment is to?"),
            "The correct procedure after completing a laboratory experiment "
            "is to @placeholder ."
        )

    def test_along_with(self):
        self.assertEqual(
            QTS.process("Along with autopsies what is it erroneously believed "
                        "that the medieval Church forbade?"),
            "It erroneously believed that the medieval Church forbade is "
            "@placeholder ( along with autopsies ) ."
        )
        self.assertEqual(
            QTS.process("Along with Aragon and Castile what Christian kingdom "
                        "was present on the Iberian Peninsula?"),
            "Present on the Iberian Peninsula was @placeholder ( along with "
            "Aragon and Castile ) ( Christian kingdom ) ."
        )
        self.assertEqual(
            QTS.process("Along with Duccio what Italian artist was a noted "
                        "innovator in this period?"),
            "A noted innovator in this period was @placeholder ( along with "
            "Duccio ) ( Italian artist ) ."
        )
        self.assertEqual(
            QTS.process("Along with Richard Marx, Bonnie Tyler, George "
                        "Michael, Phil Collins and Laura Branigan what "
                        "artist was also frequently played on Contemporary "
                        "Hit Radio stations?"),
            "@placeholder ( along with Richard Marx , Bonnie Tyler , George "
            "Michael , Phil Collins and Laura Branigan ) ( artist ) also "
            "frequently was played on Contemporary Hit Radio stations ."
        )
        self.assertEqual(
            QTS.process("Along with Richard Marx, Bonnie Tyler, George "
                        "Michael, Phil Collins and Laura Branigan, what "
                        "artist was also frequently played on Contemporary "
                        "Hit Radio stations?"),
            "@placeholder ( along with Richard Marx , Bonnie Tyler , George "
            "Michael , Phil Collins and Laura Branigan ) ( artist ) also "
            "frequently was played on Contemporary Hit Radio stations ."
        )
        self.assertEqual(
            QTS.process("Along with Duccio , what Italian artist was a noted "
                        "innovator in this period?"),
            "A noted innovator in this period was @placeholder ( along with "
            "Duccio ) ( Italian artist ) ."
        )
        self.assertEqual(
            QTS.process("Along with Turkey, France and Italy where did "
                        "expelled Spanish Jews travel to?"),
            "Expelled Spanish Jews travel to @placeholder ( along with "
            "Turkey , France and Italy ) ."
        )
        self.assertEqual(
            QTS.process("Along with Standard Average European from what "
                        "concept was Interlingua derived?"),
            "@placeholder ( along with Standard Average European from ) "
            "( concept ) Interlingua was derived ."
        )
        self.assertEqual(
            QTS.process("Along with law and finance, what is a major "
                        "component of Richmond's economy?"),
            "A major component of Richmond 's economy is @placeholder "
            "( along with law and finance ) ."
        )
        self.assertEqual(
            QTS.process("Along with Charles, who was the son of Pippin?"),
            "@placeholder ( along with Charles ) was the son of Pippin ."
        )

        # These may fail when new question types are added.
        self.assertEqual(
            QTS.process("Along with Standard Average European, from what "
                        "concept was Interlingua derived?"),
            "@placeholder ( along with Standard Average European ) from "
            "what concept was Interlingua derived ."
        )
        self.assertEqual(
            QTS.process("Along with Cooley from whose work did Scheff "
                        "derive social bond theory?"),
            "@placeholder ( along with Cooley ) from whose work did Scheff "
            "derive social bond theory ."
        )
        self.assertEqual(
            QTS.process("Along with Germany, England, Spain and Australia "
                        "where has a research center on the history of "
                        "emotions recently opened?"),
            "@placeholder ( along with Germany , England , Spain and "
            "Australia ) where has a research center on the history of "
            "emotions recently opened ."
        )
        self.assertEqual(
            QTS.process("Along with the Nicene Creed, which other Christian "
                        "creed asserts the Virgin birth of Jesus?"),
            "@placeholder ( along with the Nicene Creed ) ( other Christian "
            "creed ) asserts the Virgin birth of Jesus ."
        )
        # END

        self.assertEqual(
            QTS.process("Along with its political corruption, why did Forbes "
                        "call Miami the country's second most miserable city "
                        "in 2011?"),
            "Forbes called Miami the country 's second most miserable city in "
            "2011 because @placeholder ( along with its political corruption "
            ") ."
        )
        self.assertEqual(
            QTS.process("Along with wedding receptions, when is xalwo often "
                        "consumed?"),
            "Xalwo often is consumed on @placeholder ( along with wedding "
            "receptions ) ."
        )
        self.assertEqual(
            QTS.process("Along with hygroscopic, cellular, and anisotropic, "
                        "how is the material of wood described?"),
            "The material of wood is described as @placeholder ( along with "
            "hygroscopic , cellular , and anisotropic ) ."
        )
        self.assertEqual(
            QTS.process("Along with Manchuria, where did trade reach as far "
                        "as?"),
            "Trade reach as far as @placeholder ( along with Manchuria ) ."
        )
        self.assertEqual(
            QTS.process("Along with the Senussi, who was purged from the "
                        "military?"),
            "@placeholder ( along with the Senussi ) was purged from the "
            "military ."
        )
        self.assertEqual(
            QTS.process("Along with the Senussi who was purged from the "
                        "military?"),
            "@placeholder ( along with the Senussi ) was purged from the "
            "military ."
        )

    def test_accord_to(self):
        self.assertEqual(
            QTS.process("According to Genshin, who has the power to "
                        "destroy karma?"),
            "@placeholder ( according to Genshin ) has the power to "
            "destroy karma ."
        )
        self.assertEqual(
            QTS.process("According to The Brookings Institution report in "
                        "June 2009, how much growth did U.S. consumption "
                        "account for between 2000 and 2007?"),
            "@placeholder ( according to The Brookings Institution report "
            "in June 2009 ) growth did U.S. consumption account for "
            "between 2000 and 2007 ."
        )
        self.assertEqual(
            QTS.process("According to the Federal Constitution, how many "
                        "cantons are equal in status?"),
            "@placeholder ( according to the Federal Constitution ) cantons "
            "are equal in status ."
        )
        self.assertEqual(
            QTS.process("According to Southern Living, what are the three "
                        "best restaurants in Richmond?"),
            "The three best restaurants in Richmond are @placeholder ( "
            "according to Southern Living ) ."
        )
        self.assertEqual(
            QTS.process("According to a GRTC report, what is an example of "
                        "what most of its riders lack?"),
            "An example of what most of its riders lack is @placeholder "
            "( according to a GRTC report ) ."
        )
        self.assertEqual(
            QTS.process("According to early texts, when was Gautama born?"),
            "Gautama was born on @placeholder ( according to early texts ) ."
        )
        self.assertEqual(
            QTS.process("According to the rule of law, who must obey the "
                        "laws?"),
            "@placeholder ( according to the rule of law ) must obey the "
            "laws ."
        )
        self.assertEqual(
            QTS.process("According to Miss Maudie, which bird is never "
                        "harmful?"),
            "@placeholder ( according to Miss Maudie ) ( bird ) is never "
            "harmful ."
        )
        self.assertEqual(
            QTS.process("According to early texts, where was George born?"),
            "George was born in @placeholder ( according to early texts ) ."
        )
        self.assertEqual(
            QTS.process("According to many western countries, why did "
                        "authorities detain an unknown number "
                        "of people?"),
            "Authorities detained an unknown number of people because "
            "@placeholder ( according to many western countries ) ."
        )

        # These may change when new types are added.
        self.assertEqual(
            QTS.process("According to Asita, how would Siddhartha decide "
                        "which path to take in life?"),
            "@placeholder ( according to Asita ) how would Siddhartha decide "
            "which path to take in life ."
        )
        self.assertEqual(
            QTS.process("According to Panini, from where did Sanskrit "
                        "evolve?"),
            "@placeholder ( according to Panini ) from where did Sanskrit "
            "evolve ."
        )
        self.assertEqual(
            QTS.process("According to research findings, does Internet use "
                        "have a positive or negative effect on teen "
                        "physical health?"),
            "@placeholder ( according to research findings ) does Internet "
            "use have a positive or negative effect on teen physical health ."
        )
        self.assertEqual(
            QTS.process("According to research findings does Internet use "
                        "have a positive or negative effect on teen "
                        "physical health?"),
            "@placeholder ( according to research findings ) does Internet "
            "use have a positive or negative effect on teen physical health ."
        )

    def test_on_what(self):
        self.assertEqual(
            QTS.process("On what holiday do insurgents plan to detonate a "
                        "bomb?"),
            "Insurgents plan to detonate a bomb on @placeholder ( holiday ) ."
        )
        self.assertEqual(
            QTS.process("On what day in May does the Brotherhood and Unity "
                        "relay race end?"),
            "The Brotherhood and Unity relay race end on @placeholder "
            "( day in May ) ."
        )
        self.assertEqual(
            QTS.process("On what day did the Spanish see the island they "
                        "named Corrales?"),
            "The Spanish saw the island they named Corrales on "
            "@placeholder ( day ) ."
        )
        self.assertEqual(
            QTS.process("On what day in 2008 did the Marshall Island "
                        "government declare a state of emergency?"),
            "The Marshall Island government declared a state of emergency "
            "on @placeholder ( day in 2008 ) ."
        )
        self.assertEqual(
            QTS.process("On what date did Delacroix write a letter based on "
                        "his visit at Nohant?"),
            "Delacroix wrote a letter based on his visit at Nohant on "
            "@placeholder ( date ) ."
        )
        self.assertEqual(
            QTS.process("On what TV station did Red Nose Day appear?"),
            "Red Nose Day appeared on @placeholder ( TV station ) ."
        )
        self.assertEqual(
            QTS.process("On what date did a rescue helicopter crash with "
                        "no survivors?"),
            "A rescue helicopter crashed with no survivors on @placeholder "
            "( date ) ."
        )
        self.assertEqual(
            QTS.process("On what date did Plymouth's county status end?"),
            "Plymouth 's county status ended on @placeholder ( date ) ."
        )
        self.assertEqual(
            QTS.process("On what century did Plymouth's county status end?"),
            "Plymouth 's county status ended on @placeholder ( century ) ."
        )
        self.assertEqual(
            QTS.process("On what date was Beyonce born?"),
            "Beyonce was born on @placeholder ( date ) ."
        )
        self.assertEqual(
            QTS.process("On what geographic feature was KU built?"),
            "KU was built on @placeholder ( geographic feature ) ."
        )
        self.assertEqual(
            QTS.process("On what geographic feature is KU built?"),
            "KU is built on @placeholder ( geographic feature ) ."
        )
        self.assertEqual(
            QTS.process("On what date is Twilight Princess HD scheduled "
                        "for Australian release?"),
            "Twilight Princess HD is scheduled for Australian release "
            "on @placeholder ( date ) ."
        )
        self.assertEqual(
            QTS.process("On what date was Spectre first shown for general "
                        "audiences?"),
            "Spectre first was shown for general audiences on "
            "@placeholder ( date ) ."
        )
        self.assertEqual(
            QTS.process("On what day and month was Spectre released to the "
                        "Chinese market?"),
            "Spectre was released to the Chinese market on @placeholder "
            "( day and month ) ."
        )
        self.assertEqual(
            QTS.process("On what island is New York City's highest point "
                        "located?"),
            "New York City 's highest point is located on @placeholder "
            "( island ) ."
        )
        self.assertEqual(
            QTS.process("On what day was the funeral of Donda West?"),
            "The funeral of Donda West was on @placeholder ( day ) ."
        )
        self.assertEqual(
            QTS.process("On what season was Kristy Lee Cook a contestant "
                        "on American Idol?"),
            "Kristy Lee Cook a contestant on American Idol was on "
            "@placeholder ( season ) ."
        )
        self.assertEqual(
            QTS.process("On what part of newer iPods can you find "
                        "the buttons?"),
            "You can find the buttons on @placeholder ( part of newer "
            "iPods ) ."
        )
        self.assertEqual(
            QTS.process("On what day was the funeral of Donda West?"),
            "The funeral of Donda West was on @placeholder ( day ) ."
        )

    def test_start_with_noun(self):
        self.assertEqual(
            QTS.process("Animals that consume parts of their prey are "
                        "considered to be?"),
            "Animals that consume parts of their prey are considered "
            "to be @placeholder ."
        )
        self.assertEqual(
            QTS.process("Species that rely on few or a single prey are "
                        "called?"),
            "Species that rely on few or a single prey are "
            "called @placeholder ."
        )
        self.assertEqual(
            QTS.process("Pewter is mostly made up of"),
            "Pewter is mostly made up of @placeholder ."
        )
        self.assertEqual(
            QTS.process("Pewter is mostly made up of ..."),
            "Pewter is mostly made up of @placeholder ."
        )
        self.assertEqual(
            QTS.process("Pewter is mostly made up of?"),
            "Pewter is mostly made up of @placeholder ."
        )
        self.assertEqual(
            QTS.process("Jazz became popular during which decade in NYC?"),
            "Jazz became popular during @placeholder decade in NYC ."
        )
        self.assertEqual(
            QTS.process("People selected dogs they wanted based on what "
                        "two things?"),
            "People selected dogs they wanted based on @placeholder "
            "two things ."
        )
        self.assertEqual(
            QTS.process("Lamps and light fixtures are a form of what?"),
            "Lamps and light fixtures are a form of @placeholder ."
        )
        self.assertEqual(
            QTS.process("Scholars do not make claims without evidence about "
                        "who's life?"),
            "Scholars do not make claims without evidence about @placeholder "
            "'s life ."
        )
        self.assertEqual(
            QTS.process("Birds live on how many continents?"),
            "Birds live on @placeholder continents ."
        )
        self.assertEqual(
            QTS.process("Mimicry complexes are usually found where?"),
            "Mimicry complexes are usually found @placeholder ."
        )
        self.assertEqual(
            QTS.process("Orlam clans crossed which river to migrate "
                        "to Namibia?"),
            "Orlam clans crossed @placeholder river to migrate to Namibia ."
        )
        self.assertEqual(
            QTS.process("Beyonce got married in 2008 to whom?"),
            "Beyonce got married in 2008 to @placeholder ."
        )
        self.assertEqual(
            QTS.process("Sameness of length must be set how?"),
            "Sameness of length must be set @placeholder ."
        )
        self.assertEqual(
            QTS.process("Scout defined people doing the best they could with "
                        "what they had as who?"),
            "Scout defined people doing the best they could with what they "
            "had as @placeholder ."
        )
        self.assertEqual(
            QTS.process("Scout defined people doing the best they could with "
                        "what they had as who"),
            "Scout defined people doing the best they could with what they "
            "had as @placeholder ."
        )
        self.assertEqual(
            QTS.process("Scout defined people doing the best they could with "
                        "what they had as who."),
            "Scout defined people doing the best they could with what they "
            "had as @placeholder ."
        )
        self.assertEqual(
            QTS.process("Insects show how toxic they are with what kind of "
                        "colors?"),
            "Insects show how toxic they are with @placeholder kind of "
            "colors ."
        )
        self.assertEqual(
            QTS.process("Vaccination is a way in which what may be acquired?"),
            "Vaccination is a way in which @placeholder may be acquired ."
        )
        self.assertEqual(
            QTS.process("Politicians who were at the end of their political "
                        "careers were offered what kind of position with "
                        "companies they were involved with politically?"),
            "Politicians who were at the end of their political careers were "
            "offered @placeholder kind of position with companies they were "
            "involved with politically ."
        )

    def test_start_with_proper_noun(self):
        self.assertEqual(
            QTS.process("Mrigavyadha means what?"),
            "Mrigavyadha means @placeholder ."
        )
        self.assertEqual(
            QTS.process("Beyonce's grandma's name was?"),
            "Beyonce 's grandma 's name was @placeholder ."
        )
        self.assertEqual(
            QTS.process("Chopin was attracted to?"),
            "Chopin was attracted to @placeholder ."
        )
        self.assertEqual(
            QTS.process("Chopin was attracted to ..."),
            "Chopin was attracted to @placeholder ."
        )
        self.assertEqual(
            QTS.process("Chopin was attracted to"),
            "Chopin was attracted to @placeholder ."
        )
        self.assertEqual(
            QTS.process("Chopin was attracted to."),
            "Chopin was attracted to @placeholder ."
        )
        self.assertEqual(
            QTS.process("Italy is what?"),
            "Italy is @placeholder ."
        )
        self.assertEqual(
            QTS.process("Spain refers to a university in what other way?"),
            "Spain refers to a university in @placeholder other way ."
        )
        self.assertEqual(
            QTS.process("Youtube is ranked what on the world's list of most "
                        "visited sites?"),
            "Youtube is ranked @placeholder on the world 's list of most "
            "visited sites ."
        )
        self.assertEqual(
            QTS.process("Youtube is ranked what on the world's list of most "
                        "visited sites"),
            "Youtube is ranked @placeholder on the world 's list of most "
            "visited sites ."
        )
        self.assertEqual(
            QTS.process("Arizona is south of which river?"),
            "Arizona is south of @placeholder river ."
        )
        self.assertEqual(
            QTS.process("Greece is one of the members who founded what "
                        "organization?"),
            "Greece is one of the members who founded @placeholder "
            "organization ."
        )
        self.assertEqual(
            QTS.process("Feynman borrowed a car from Klaus Fuchs, who was "
                        "later found to be a what?"),
            "Feynman borrowed a car from Klaus Fuchs , who was later found "
            "to be a @placeholder ."
        )
        self.assertEqual(
            QTS.process("Vipassana meditation can reveal how the mind "
                        "was what"),
            "Vipassana meditation can reveal how the mind was @placeholder ."
        )

    def test_start_with_A(self):
        self.assertEqual(
            QTS.process("A New Hope' said to be similar to?"),
            "A New Hope ' said to be similar to @placeholder ."
        )
        self.assertEqual(
            QTS.process("A modern piano is generally what?"),
            "A modern piano is generally @placeholder ."
        )
        self.assertEqual(
            QTS.process("A modern piano is generally what"),
            "A modern piano is generally @placeholder ."
        )
        self.assertEqual(
            QTS.process("A modern piano is generally what ..."),
            "A modern piano is generally @placeholder ."
        )
        self.assertEqual(
            QTS.process("A modern piano is generally what."),
            "A modern piano is generally @placeholder ."
        )
        self.assertEqual(
            QTS.process("A dog with countershading has dark coloring where?"),
            "A dog with countershading has dark coloring @placeholder ."
        )
        self.assertEqual(
            QTS.process("A treaty requiring local prosecution by a party for "
                        "particular crimes is an example of which type "
                        "of treaty?"),
            "A treaty requiring local prosecution by a party for particular "
            "crimes is an example of @placeholder type of treaty ."
        )
        self.assertEqual(
            QTS.process("A zero inflation policy would limit who's influence "
                        "and ability to react?"),
            "A zero inflation policy would limit @placeholder 's influence "
            "and ability to react ."
        )
        self.assertEqual(
            QTS.process("A lot of Greece was lost by whom in the 14th "
                        "century?"),
            "A lot of Greece was lost by @placeholder in the 14th century ."
        )
        self.assertEqual(
            QTS.process("A lot of American common law diverged from where?"),
            "A lot of American common law diverged from @placeholder ."
        )
        self.assertEqual(
            QTS.process("A research found how many different species of "
                        "plants native to the island?"),
            "A research found @placeholder different species of plants native "
            "to the island ."
        )
        self.assertEqual(
            QTS.process("A detached knot will probably drop out of the wood "
                        "when someone saws it into what?"),
            "A detached knot will probably drop out of the wood when someone "
            "saws it into @placeholder ."
        )
        self.assertEqual(
            QTS.process("A typical trade off when creating an MP3 file is "
                        "between the amount of space used and what "
                        "other factor?"),
            "A typical trade off when creating an MP3 file is between the "
            "amount of space used and @placeholder other factor ."
        )

    def test_how_advj(self):
        self.assertEqual(
            QTS.process("How lond did the creation of Red Book CD-DA "
                        "standard take?"),
            "@placeholder lond did the creation of Red Book CD - DA "
            "standard take ."
        )
        self.assertEqual(
            QTS.process("How far back to San Diego's roots in the arts and "
                        "theater sector go?"),
            "@placeholder far back to San Diego 's roots in the arts and "
            "theater sector go ."
        )
        self.assertEqual(
            QTS.process("How often does the XPT to Sydney depart?"),
            "The XPT to Sydney depart @placeholder ( often ) ."
        )
        self.assertEqual(
            QTS.process("How often do temperatures on the coastal plain of "
                        "NC drop below freezing at night?"),
            "Temperatures on the coastal plain of NC drop below freezing at "
            "night @placeholder ( often ) ."
        )
        self.assertEqual(
            QTS.process("How often does the British-Irish Council meet?"),
            "The British - Irish Council meet @placeholder ( often ) ."
        )
        self.assertEqual(
            QTS.process("How often do the national rugby teams play for the "
                        "Triple Crown?"),
            "The national rugby teams play for the Triple Crown "
            "@placeholder ( often ) ."
        )
        self.assertEqual(
            QTS.process("How high did Kyriakos Ioannou jump in Osaka "
                        "in 2007?"),
            "Kyriakos Ioannou jumped in Osaka in 2007 @placeholder ( high ) ."
        )
        self.assertEqual(
            QTS.process("How far did a Manx shearwater fly over it's "
                        "lifespan?"),
            "A Manx shearwater flew over it 's lifespan @placeholder ( far ) ."
        )
        self.assertEqual(
            QTS.process("How far back could these recording practices be "
                        "traced?"),
            "These recording practices could be traced @placeholder ( "
            "far back ) ."
        )
        self.assertEqual(
            QTS.process("How high could the temperatures have risen to cause "
                        "the melting?"),
            "The temperatures could have risen @placeholder ( high ) to cause "
            "the melting ."
        )
        self.assertEqual(
            QTS.process("How large will the two Queen Elizabeth ships be?"),
            "The two Queen Elizabeth ships will be @placeholder ( large ) ."
        )
        self.assertEqual(
            QTS.process("How high had cotton revenues risen by the time of "
                        "the American Civil War?"),
            "Cotton revenues had risen @placeholder ( high ) by the time of "
            "the American Civil War ."
        )
        self.assertEqual(
            QTS.process("How far back can dog training be found?"),
            "Dog training can be found @placeholder ( far back ) ."
        )
        self.assertEqual(
            QTS.process("How far away has a trumpeter been known to stand?"),
            "A trumpeter has been known @placeholder ( far away ) to stand ."
        )
        self.assertEqual(
            QTS.process("How numerous would the number of races be if one "
                        "gene can distinguish races?"),
            "The number of races would be @placeholder ( numerous ) if one g"
            "ene can distinguish races ."
        )
        self.assertEqual(
            QTS.process("How large in square kilometers is Greater "
                        "Hyderabad?"),
            "Greater Hyderabad is @placeholder ( large in square "
            "kilometers ) ."
        )
        self.assertEqual(
            QTS.process("How simple is the process of transformation?"),
            "The process of transformation is @placeholder ( simple ) ."
        )
        self.assertEqual(
            QTS.process("How large is Notre Dame in acres?"),
            "Notre Dame in acres is @placeholder ( large ) ."
        )
        self.assertEqual(
            QTS.process("How large is Kathmandu in terms of square miles?"),
            "Kathmandu is @placeholder ( large ) in terms of square miles ."
        )
        self.assertEqual(
            QTS.process("How old was Schwarzenegger when he won "
                        "Mr. Universe?"),
            "Schwarzenegger was @placeholder ( old ) when he won Mr. "
            "Universe ."
        )
        self.assertEqual(
            QTS.process("How big was the rocket that was introduced to handle "
                        "dive bombing attacks?"),
            "The rocket that was introduced to handle dive bombing attacks "
            "was @placeholder ( big ) ."
        )
        self.assertEqual(
            QTS.process("Who far from the center of London is London "
                        "Heathrow Airport?"),
            "@placeholder far from the center of London is London "
            "Heathrow Airport ."
        )
        self.assertEqual(
            QTS.process("How near to the epicenter was the power plant?"),
            "The power plant was @placeholder ( near to the epicenter ) ."
        )
        self.assertEqual(
            QTS.process("How far away from the line of scrimmage must "
                        "Canadian football defenders be?"),
            "Canadian football defenders must be @placeholder ( far away "
            "from the line of scrimmage ) ."
        )

    def test_which_verb(self):
        self.assertEqual(
            QTS.process("Which can be regarded as the most interesting "
                        "project?"),
            "@placeholder can be regarded as the most interesting project ."
        )
        self.assertEqual(
            QTS.process("Which cannot be regarded as the most interesting "
                        "project?"),
            "@placeholder can not be regarded as the most interesting "
            "project ."
        )
        self.assertEqual(
            QTS.process("Which can small mutations be caused by?"),
            "Small mutations can be caused by @placeholder ."
        )
        self.assertEqual(
            QTS.process("Which may be regarded as the most interesting "
                        "project?"),
            "@placeholder may be regarded as the most interesting project ."
        )
        self.assertEqual(
            QTS.process("Which must be regarded as the most interesting "
                        "project?"),
            "@placeholder must be regarded as the most interesting project ."
        )
        self.assertEqual(
            QTS.process("Which measures the potential development, the HDI "
                        "or the IHDI?"),
            "@placeholder measures the potential development , the HDI or "
            "the IHDI ."
        )
        self.assertEqual(
            QTS.process("Which elected official had imperium powers?"),
            "@placeholder elected official had imperium powers ."
        )

    def test_which_general(self):
        self.assertEqual(
            QTS.process("Which historic great players have played at "
                        "Yankee Stadium?"),
            "@placeholder ( historic great players ) have played at "
            "Yankee Stadium ."
        )
        self.assertEqual(
            QTS.process("Which European nationality first explored the "
                        "Tennessee region?"),
            "@placeholder ( European nationality ) first explored the "
            "Tennessee region ."
        )
        self.assertEqual(
            QTS.process("Which World Cup did Brasilia host?"),
            "@placeholder ( World Cup ) did Brasilia host ."
        )
        self.assertEqual(
            QTS.process("Which World Fair was hosted in San Diego in 1935?"),
            "Hosted in San Diego in 1935 was @placeholder ( World Fair ) ."
        )
        self.assertEqual(
            QTS.process("Which major river is located west of the Appalachian "
                        "mountains?"),
            "Located west of the Appalachian mountains is @placeholder "
            "( major river ) ."
        )
        self.assertEqual(
            QTS.process("Which Secretary of State attended Notre Dame?"),
            "@placeholder Secretary of State attended Notre Dame ."
        )
        self.assertEqual(
            QTS.process("Which Notre Dame alum from the College of Science "
                        "won a Nobel Prize?"),
            "@placeholder ( Notre Dame alum from the College of Science ) won "
            "a Nobel Prize ."
        )
        self.assertEqual(
            QTS.process("Which typically has thicker skin, dogs or wolves?"),
            "@placeholder ( typically ) has thicker skin , dogs or wolves ."
        )
        self.assertEqual(
            QTS.process("Which Tucson street is devoted to bicycles?"),
            "Devoted to bicycles is @placeholder ( Tucson street ) ."
        )
        self.assertEqual(
            QTS.process("Which two Spaniards aided this colonization and "
                        "started the first catholic church?"),
            "@placeholder ( two Spaniards ) aided this colonization and "
            "started the first catholic church ."
        )
        self.assertEqual(
            QTS.process("Which former co-host of CBS's The Early Show "
                        "graduated from BYU?"),
            "@placeholder ( former co - host ) graduated from BYU ."
        )
        self.assertEqual(
            QTS.process("Which Ratchet & Clank title debuted at E3 2007?"),
            "@placeholder ( Ratchet & Clank ) ( title ) debuted at E3 2007 ."
        )
        self.assertEqual(
            QTS.process("Which prime minister was appointed only one time?"),
            "Appointed only one time was @placeholder ( prime minister ) ."
        )
        self.assertEqual(
            QTS.process("Which two Asian countries have started to adopt the "
                        "rule of law?"),
            "@placeholder ( two Asian countries ) have started to adopt the "
            "rule of law ."
        )
        self.assertEqual(
            QTS.process("Which former U.S. president has been born in "
                        "New Haven?"),
            "@placeholder ( former U.S. president ) has been born in New "
            "Haven ."
        )
        self.assertEqual(
            QTS.process("Which Protestant churches still honor Mary?"),
            "@placeholder ( Protestant churches ) still honor Mary ."
        )

    def test_in_smth_question(self):
        self.assertEqual(
            QTS.process("In 2007, which airlines made deals to include iPod "
                        "connections on their planes?"),
            "@placeholder ( airlines ) made deals to include iPod connections "
            "on their planes , in 2007 ."
        )
        self.assertEqual(
            QTS.process("In 2014, what did the census estimate the population "
                        "of New York City to be?"),
            "The census estimate the population of New York City to be , in "
            "2014 @placeholder ."
        )
        self.assertEqual(
            QTS.process("In the early 1920s, what was the second most highly "
                        "populated city in the world?"),
            "The second most highly populated city in the world , in the "
            "early 1920s was @placeholder ."
        )
        self.assertEqual(
            QTS.process("In the first half of 2010, what percentage of "
                        "shooting victims were African-American or Hispanic?"),
            "@placeholder ( percentage of shooting victims ) were African - "
            "American or Hispanic , in the first half of 2010 ."
        )
        self.assertEqual(
            QTS.process("In the waning years of the Malla dynasty, what "
                        "fortified cities existed in the Kathmandu Valley?"),
            "@placeholder fortified cities existed in the Kathmandu Valley , "
            "in the waning years of the Malla dynasty ."
        )
        self.assertEqual(
            QTS.process("In areas of strict enforcement, what happened to "
                        "Christians?"),
            "@placeholder happened to Christians , in areas of strict "
            "enforcement ."
        )
        self.assertEqual(
            QTS.process("In the 5th century what was the capital of the "
                        "Western Roman Empire?"),
            "The capital of the Western Roman Empire , in the 5th century was "
            "@placeholder ."
        )
        self.assertEqual(
            QTS.process("In the place where nothing happens, what is the most "
                        "interesting place?"),
            "The most interesting place , in the place where nothing happens "
            "is @placeholder ."
        )
        self.assertEqual(
            QTS.process("In front of which committee did Powell testify?"),
            "@placeholder ( committee ) Powell testified , in front of ."
        )
        self.assertEqual(
            QTS.process("In general, what does immunology study?"),
            "Immunology study , in general @placeholder ."
        )
        self.assertEqual(
            QTS.process("In enforcing a charge of genocide, what loophole do "
                        "many of the signatories possess?"),
            "@placeholder ( loophole ) many of the signatories possess , in "
            "enforcing a charge of genocide ."
        )
        self.assertEqual(
            QTS.process("In degrees Fahrenheit, what is Plymouth's annual "
                        "mean temperature?"),
            "Plymouth 's annual mean temperature , in degrees Fahrenheit is "
            "@placeholder ."
        )
        self.assertEqual(
            QTS.process("In terms of Swaziland, what does SNL refer to?"),
            "SNL refer to , in terms of Swaziland @placeholder ."
        )
        self.assertEqual(
            QTS.process("In 2009, Beyonce started her second world tour and "
                        "grossed how much money?"),
            "Beyonce started her second world tour and grossed @placeholder "
            "much money , in 2009 ."
        )
        self.assertEqual(
            QTS.process("In 2006 Youtube found that the majority of longer "
                        "videos were what?"),
            "Youtube found that the majority of longer videos were "
            "@placeholder , in 2006 ."
        )
        self.assertEqual(
            QTS.process("In 2009, what percent of the players were English "
                        "in the Premier League?"),
            "@placeholder ( percent of the players ) were English in the "
            "Premier League , in 2009 ."
        )

    def test_start_with_be(self):
        self.assertEqual(
            QTS.process("Is the Apple SDK available to third-party game "
                        "publishers?"),
            "The Apple SDK is available to third - party game publishers - "
            "@placeholder ( true or false ) ."
        )
        self.assertEqual(
            QTS.process("Was the new Count of Oeiras opposed by anyone after "
                        "the Tavora affair?"),
            "The new Count of Oeiras was opposed by anyone after the Tavora "
            "affair - @placeholder ( true or false ) ."
        )
        self.assertEqual(
            QTS.process("Are immune tissues typically fixed with specific "
                        "organs usually?"),
            "Immune tissues typically are fixed with specific organs usually "
            "- @placeholder ( true or false ) ."
        )
        self.assertEqual(
            QTS.process("Is \"low\" voltage used by trains safe for people?"),
            "\" low \" voltage is used by trains safe for people - "
            "@placeholder ( true or false ) ."
        )
        self.assertEqual(
            QTS.process("Is there a single standard for HDTV color support?"),
            "There is a single standard for HDTV color support - @placeholder "
            "( true or false ) ."
        )
        self.assertEqual(
            QTS.process("Are large jungle cats part of the animal population "
                        "of Burma?"),
            "Large jungle cats are part of the animal population of Burma - "
            "@placeholder ( true or false ) ."
        )
        self.assertEqual(
            QTS.process("Was the Chopin family boarding house for male or "
                        "female students?"),
            "The Chopin family was boarding house for @placeholder ( male or "
            "female ) students ."
        )
        self.assertEqual(
            QTS.process("Is balsa a softwood, iron or a hardwood?"),
            "Balsa is a @placeholder ( softwood , iron or a hardwood ) ."
        )
        self.assertEqual(
            QTS.process("Are British and American English regarded as "
                        "distinct languages, or dialects of a single "
                        "language?"),
            "British and American English are regarded @placeholder ( as "
            "distinct languages , or dialects of ) a single language ."
        )
        self.assertEqual(
            QTS.process("Is the Premier League the most watched football "
                        "league in the world?"),
            "The Premier League is the most watched football league "
            "in the world - @placeholder ( true or false ) ."
        )
        self.assertEqual(
            QTS.process("Is the color difference between heartwood and "
                        "sapwood usually very subtle or conspicuous?"),
            "The color difference between heartwood and sapwood is usually "
            "very @placeholder ( subtle or conspicuous ) ."
        )

    def test_start_with_this(self):
        self.assertEqual(
            QTS.process("This decision reflected a revision of what?"),
            "This decision reflected a revision of @placeholder ."
        )
        self.assertEqual(
            QTS.process("This decision reflected a revision of what??"),
            "This decision reflected a revision of @placeholder ."
        )
        self.assertEqual(
            QTS.process("This decision reflected a revision of what"),
            "This decision reflected a revision of @placeholder ."
        )
        self.assertEqual(
            QTS.process("This decision reflected a revision of what."),
            "This decision reflected a revision of @placeholder ."
        )
        self.assertEqual(
            QTS.process("This separate service was known as what in "
                        "the Soviet Union?"),
            "This separate service was known as @placeholder in the "
            "Soviet Union ."
        )
        self.assertEqual(
            QTS.process("This was the biggest display of mourning since "
                        "the death of who?"),
            "This was the biggest display of mourning since the death of "
            "@placeholder ."
        )
        self.assertEqual(
            QTS.process("This body makes provisions in respect to matters "
                        "concerning whom?"),
            "This body makes provisions in respect to matters concerning "
            "@placeholder ."
        )
        self.assertEqual(
            QTS.process("This observation best supports which statement?"),
            "This observation best supports @placeholder statement ."
        )
        self.assertEqual(
            QTS.process("This means that ..."),
            "This means that @placeholder ."
        )
        self.assertEqual(
            QTS.process("This means that ..."),
            "This means that @placeholder ."
        )
        self.assertEqual(
            QTS.process("This is because most of the energy in the "
                        "gasoline is"),
            "This is because most of the energy in the gasoline is "
            "@placeholder ."
        )
