import { Box, SimpleGrid } from "@chakra-ui/react";
import { Link, useLocation } from "react-router-dom";

const menuStyle = {
  display: "block",
  padding: "0.5em",
};

export const SideBar: React.FunctionComponent<{}> = () => {
  const selectedColor = ["teal.50", "black", "true"];
  let pagesColor = ["teal.500", "white", "false"];
  let sitesColor = ["teal.500", "white", "false"];
  const location = useLocation();
  if (
    location.pathname.startsWith("/admin/page") ||
    location.pathname == "/admin/"
  ) {
    pagesColor = selectedColor;
  } else if (location.pathname.startsWith("/admin/site")) {
    sitesColor = selectedColor;
  } else {
    return <></>;
  }

  return (
    <Box
      minWidth={250}
      height="calc(100vh - 90px)"
      bgColor="teal.300"
      color="white"
    >
      <SimpleGrid columns={1} spacing={1}>
        <Box
          bg={pagesColor[0]}
          borderRadius="md"
          color={pagesColor[1]}
          margin={2}
          marginBottom={0}
        >
          <Link
            to="/admin/pages"
            style={menuStyle}
            data-selected={pagesColor[2]}
          >
            Pages
          </Link>
        </Box>
        <Box
          bg={sitesColor[0]}
          borderRadius="md"
          color={sitesColor[1]}
          margin={2}
          marginBottom={0}
        >
          <Link
            to="/admin/sites"
            style={menuStyle}
            data-selected={sitesColor[2]}
          >
            Sites
          </Link>
        </Box>
      </SimpleGrid>
    </Box>
  );
};
