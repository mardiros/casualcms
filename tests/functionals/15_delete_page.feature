Feature: As a user, I can delete page

  Scenario: Can't delete a page if there are child pages
    Given user on the admin page
    And a "/home" page of type "blog:HomePage"
    And a "/home/cat" page of type "blog:CategoryPage"
    When I visit "/admin/pages/?parent=/home"
    Then I see the text "Add new page"
    And I don't see the text "Delete this page"

  Scenario: Can delete a page if there are no child pages
    Given user on the admin page
    And a "/home" page of type "blog:HomePage"
    When I visit "/admin/pages/?parent=/home"
    Then I see the text "Add new page"
    When I click on the "Delete this page" button
    And I click on the "Confirm Deletion" button
    Then I see the text "Add new page"
    And I don't see the text "home"
